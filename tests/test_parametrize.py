"""Tests for pytest parametrize functionality with multiple input values."""

import pytest


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Parametrize")
class TestParametrize:
    """Test class for parametrize functionality."""

    @pytest.mark.parametrize(("input_value", "expected"), [(1, 1), (2, 2), (3, 3)])
    @pytest.mark.title("Parametrize test with different inputs")
    def test_parametrize(self, input_value: int, expected: int) -> None:
        """Test parametrize with multiple input values."""
        assert input_value == expected, f"Expected {expected}, got {input_value}"  # noqa: S101
