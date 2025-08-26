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


def soft_assert(condition: bool, message: str | None = None) -> bool:
    """Record a non-fatal assertion that doesn't immediately fail the test.

    Soft assertions allow tests to continue execution even when some
    assertions fail, collecting all failures for reporting at the end.

    Args:
        condition: The boolean condition to check.
        message: Optional descriptive message for the assertion.
                Defaults to "Soft assertion" if not provided.

    Returns:
        The boolean value of the condition.

    Example:
        >>> soft_assert(user.name is not None, "User should have a name")
        >>> soft_assert(user.email.endswith("@company.com"), "Email should be company domain")
    """
    msg = message or "Soft assertion"
    add_soft_check_record(msg, bool(condition))
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
