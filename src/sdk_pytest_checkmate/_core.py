"""Core functionality for test steps, soft assertions, and data attachments."""

import time
from types import TracebackType
from typing import Self

from ._context import add_data_record, add_soft_check_record, add_step_record
from ._models import DataRecord, StepRecord
from ._types import JsonData


class StepContext:
    """Context manager for recording test steps with timing information.

    This class provides both synchronous and asynchronous context manager
    protocols for recording test steps.
    """

    def __init__(self, name: str) -> None:
        """Initialize the step context.

        Args:
            name: The name of the step to be recorded.
        """
        self.name = name
        self._record: StepRecord | None = None

    def __enter__(self) -> Self:
        """Enter the synchronous context manager."""
        self._record = add_step_record(self.name)
        if self._record is not None:
            self._record.start = time.monotonic()
            self._record.end = None
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Exit the synchronous context manager.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception instance if an exception occurred.
            traceback: Traceback object if an exception occurred.

        Returns:
            False to propagate any exception that occurred.
        """
        if self._record is not None:
            self._record.finish(exc_value)
        return False

    async def __aenter__(self) -> Self:
        """Enter the asynchronous context manager."""
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Exit the asynchronous context manager.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception instance if an exception occurred.
            traceback: Traceback object if an exception occurred.

        Returns:
            False to propagate any exception that occurred.
        """
        return self.__exit__(exc_type, exc_value, traceback)


def step(name: str) -> StepContext:
    """Create a step context manager for recording test steps.

    Args:
        name: The name of the step to be recorded.

    Returns:
        A step context manager that can be used with 'with' statement.

    Example:
        >>> with step("Login user"):
        ...     # Step implementation
        ...     pass

        >>> async with step("Fetch data"):
        ...     # Async step implementation
        ...     pass
    """
    return StepContext(name)


def soft_assert(condition: bool, message: str | None = None, details: str | list[str] | None = None) -> bool:
    """Record a non-fatal assertion that doesn't immediately fail the test.

    Soft assertions allow tests to continue execution even when some
    assertions fail, collecting all failures for reporting at the end.

    Args:
        condition: The boolean condition to check.
        message: Optional descriptive message for the assertion.
                Defaults to "Soft assertion" if not provided.
        details: Optional details for the assertion. If not provided,
                the condition will be analyzed and shown with actual values.
                Can be a string or list of strings.

    Returns:
        The boolean value of the condition.

    Example:
        >>> soft_assert(user.name is not None, "User should have a name")
        >>> soft_assert(user.email.endswith("@company.com"), "Email should be company domain",
        ...            details="Checking domain validation rules")
        >>> soft_assert(len(items) > 0, "Items list should not be empty",
        ...            details=["List length check", "Validation step 1"])
    """
    msg = message or "Soft assertion"

    if details is None:
        import ast
        import inspect
        import re
        from pathlib import Path

        frame = inspect.currentframe()
        if frame and frame.f_back:
            code = frame.f_back.f_code
            filename = code.co_filename
            lineno = frame.f_back.f_lineno
            frame_locals = frame.f_back.f_locals
            frame_globals = frame.f_back.f_globals

            try:
                lines = Path(filename).read_text(encoding="utf-8").splitlines()
                if 0 <= lineno - 1 < len(lines):
                    current_line = lineno - 1
                    line_content = ""

                    while current_line >= 0:
                        current_text = lines[current_line].strip()
                        line_content = current_text + " " + line_content
                        if "soft_assert" in current_text:
                            break
                        current_line -= 1

                    next_line = lineno
                    while next_line < len(lines):
                        if line_content.count("(") <= line_content.count(")"):
                            break
                        line_content += " " + lines[next_line].strip()
                        next_line += 1

                    condition_str = None

                    match = re.search(r"soft_assert\s*\(", line_content)
                    if match:
                        start_pos = match.end() - 1  # Position of opening parenthesis
                        paren_count = 0
                        i = start_pos

                        while i < len(line_content):
                            if line_content[i] == "(":
                                paren_count += 1
                            elif line_content[i] == ")":
                                paren_count -= 1
                                if paren_count == 0:
                                    break
                            i += 1

                        if paren_count == 0:
                            args_content = line_content[start_pos + 1 : i]

                            try:
                                args_ast = ast.parse(f"f({args_content})", mode="eval")
                                if isinstance(args_ast.body, ast.Call) and args_ast.body.args:
                                    condition_str = ast.unparse(args_ast.body.args[0])
                            except Exception:
                                bracket_count = 0
                                paren_count = 0
                                brace_count = 0
                                quote_char = None

                                for j, char in enumerate(args_content):
                                    if quote_char:
                                        if char == quote_char and (j == 0 or args_content[j - 1] != "\\"):
                                            quote_char = None
                                    elif char in ('"', "'"):
                                        quote_char = char
                                    elif char == "[":
                                        bracket_count += 1
                                    elif char == "]":
                                        bracket_count -= 1
                                    elif char == "(":
                                        paren_count += 1
                                    elif char == ")":
                                        paren_count -= 1
                                    elif char == "{":
                                        brace_count += 1
                                    elif char == "}":
                                        brace_count -= 1
                                    elif (
                                        char == ","
                                        and bracket_count == 0
                                        and paren_count == 0
                                        and brace_count == 0
                                        and not quote_char
                                    ):
                                        condition_str = args_content[:j].strip()
                                        break

                                if not condition_str:
                                    condition_str = args_content.strip()

                    if condition_str:
                        try:
                            tree = ast.parse(condition_str, mode="eval")

                            if isinstance(tree.body, ast.Compare):
                                comp = tree.body
                                left_code = ast.unparse(comp.left)

                                try:
                                    left_value = eval(left_code, frame_globals, frame_locals)  # noqa: S307
                                    left_repr = repr(left_value)
                                except Exception:
                                    left_repr = left_code

                                if comp.ops and comp.comparators:
                                    op = comp.ops[0]
                                    right_code = ast.unparse(comp.comparators[0])

                                    try:
                                        right_value = eval(right_code, frame_globals, frame_locals)  # noqa: S307
                                        right_repr = repr(right_value)
                                    except Exception:
                                        right_repr = right_code

                                    op_map = {
                                        ast.Gt: ">",
                                        ast.Lt: "<",
                                        ast.GtE: ">=",
                                        ast.LtE: "<=",
                                        ast.Eq: "==",
                                        ast.NotEq: "!=",
                                        ast.Is: "is",
                                        ast.IsNot: "is not",
                                        ast.In: "in",
                                        ast.NotIn: "not in",
                                    }
                                    op_str = op_map.get(type(op), str(type(op).__name__))

                                    details = f"{condition_str} ({left_repr} {op_str} {right_repr})"
                                else:
                                    details = condition_str
                            else:
                                try:
                                    result = eval(condition_str, frame_globals, frame_locals)  # noqa: S307
                                    details = f"{condition_str} (evaluates to {result!r})"
                                except Exception:
                                    details = condition_str
                        except Exception:
                            details = condition_str
                    else:
                        details = str(condition)
                else:
                    details = str(condition)
            except OSError:
                details = str(condition)
        else:
            details = str(condition)

    add_soft_check_record(msg, bool(condition), details)
    return bool(condition)


def add_data_report(data: JsonData, label: str) -> DataRecord:
    """Attach arbitrary data to the test timeline for inspection in reports.

    Args:
        data: The data to attach. Can be any JSON-serializable object.
        label: A descriptive label for the data that appears in reports.

    Returns:
        The created data record.

    Example:
        >>> config = {"endpoint": "/api/users", "timeout": 30}
        >>> add_data_report(config, "API Configuration")

        >>> response_data = {"status": 200, "body": {"id": 123}}
        >>> add_data_report(response_data, "API Response")
    """
    return add_data_record(label, data)
