"""JSON Schema validation with soft assertions."""

import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validators
from referencing.jsonschema import EMPTY_REGISTRY

from ._constants import ERROR_NO_SCHEMA
from ._core import soft_assert
from ._types import JsonData


class JsonValidationError(Exception):
    """Custom exception for JSON validation errors."""

    def __init__(self, message: str, errors: list[str]) -> None:
        """Initialize the validation error.

        Args:
            message: The main error message.
            errors: List of specific validation errors.
        """
        super().__init__(message)
        self.errors = errors


def _load_json_schema(path: str | Path) -> dict[str, Any]:
    """Load a JSON schema from a file.

    Args:
        path: Path to the JSON schema file.

    Returns:
        The loaded JSON schema as a dictionary.

    Raises:
        FileNotFoundError: If the schema file doesn't exist.
        json.JSONDecodeError: If the schema file contains invalid JSON.
    """
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Schema file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in schema file: {path}", e.doc, e.pos) from e


def _format_validation_errors(errors: list[ValidationError]) -> list[str]:
    """Format validation errors for human-readable output.

    Args:
        errors: List of validation errors from jsonschema.

    Returns:
        List of formatted error messages.
    """
    return [f"\t- ({'/'.join(str(p) for p in error.absolute_path)}) {error.message}" for error in errors]


def _validate_json_data(data: JsonData, schema: dict[str, Any]) -> tuple[bool, str]:
    """Validate JSON data against a schema.

    Args:
        data: The data to validate.
        schema: The JSON schema to validate against.

    Returns:
        A tuple of (is_valid, error_message).
    """
    try:
        validator_class = validators.validator_for(schema)
        validator = validator_class(schema, registry=EMPTY_REGISTRY)

        validation_errors = list(validator.iter_errors(data))
        if validation_errors:
            formatted_errors = _format_validation_errors(validation_errors)
            error_message = "JSON Schema validation failed:\n" + "\n".join(formatted_errors)
            return (False, error_message)

        return (True, "JSON Schema validation passed")
    except Exception as e:
        return (False, f"JSON Schema validation error: {e}")


def validate_json_strict(
    data: JsonData,
    *,
    schema: dict[str, Any] | None = None,
    schema_path: str | Path | None = None,
) -> None:
    """Validate JSON data against a schema with strict error handling.

    Args:
        data: The JSON data to validate.
        schema: JSON Schema as a dictionary (optional).
        schema_path: Path to a JSON Schema file (optional).

    Raises:
        ValueError: If no schema is provided.
        JsonValidationError: If validation fails.
    """
    if schema is None and schema_path is not None:
        schema = _load_json_schema(schema_path)

    if schema is None:
        raise ValueError(ERROR_NO_SCHEMA)

    is_valid, error_message = _validate_json_data(data, schema)
    if not is_valid:
        validator_class = validators.validator_for(schema)
        validator = validator_class(schema, registry=EMPTY_REGISTRY)
        errors = _format_validation_errors(list(validator.iter_errors(data)))
        raise JsonValidationError(error_message, errors)


def soft_validate_json(
    data: JsonData,
    *,
    schema: dict[str, Any] | None = None,
    schema_path: str | Path | None = None,
) -> None:
    """Validate JSON data against a schema using soft assertions.

    This function performs JSON schema validation and records the result
    as a soft assertion, allowing the test to continue even if validation fails.

    Args:
        data: The JSON data to validate.
        schema: JSON Schema as a dictionary (optional, mutually exclusive with schema_path).
        schema_path: Path to a JSON Schema file (optional, used if schema is not provided).

    Raises:
        ValueError: If no schema is provided via either parameter.

    Example:
        >>> user_data = {"id": 123, "name": "John", "email": "john@example.com"}
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "id": {"type": "integer"},
        ...         "name": {"type": "string"},
        ...         "email": {"type": "string", "format": "email"}
        ...     },
        ...     "required": ["id", "name", "email"]
        ... }
        >>> soft_validate_json(user_data, schema=schema)
    """
    if schema is None and schema_path is not None:
        schema = _load_json_schema(schema_path)

    if schema is None:
        raise ValueError(ERROR_NO_SCHEMA)

    is_valid, error_message = _validate_json_data(data, schema)
    soft_assert(is_valid, error_message)
