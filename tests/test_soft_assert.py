"""Tests for soft assertion functionality and behavior with various scenarios."""

import pytest

from sdk_pytest_checkmate import soft_assert


@pytest.mark.epic("Project functionality")
@pytest.mark.story("Soft Assert Story DEMO")
class TestSoftAssert:
    """Test class for soft assertion functionality with markers."""

    @pytest.mark.title("Soft assert passed test with Markers")
    def test_soft_assert_markers_passed(self) -> None:
        """Test soft assertions that all pass successfully."""
        soft_assert(1 == 1, "1 should equal 1")
        soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Soft assert failed test with Markers")
    def test_soft_assert_markers_failed(self) -> None:
        """Test soft assertions that all fail."""
        soft_assert(1 == 2, "1 should equal 2")
        soft_assert(2 == 3, "2 should equal 3")

    @pytest.mark.title("Soft assert mixed test with Markers")
    def test_soft_assert_markers_mixed(self) -> None:
        """Test soft assertions with mixed pass and fail results."""
        soft_assert(1 == 1, "1 should equal 1")
        soft_assert(2 == 3, "2 should equal 3")
        soft_assert(2 == 2, "2 should equal 2")
        soft_assert(3 == 4, "3 should equal 4")

    @pytest.mark.title("Soft assert skip test without Markers")
    def test_soft_assert_skip(self) -> None:
        """Test demonstrating skipped soft assertion test."""
        pytest.skip("Skipping this test for demonstration purposes")
        soft_assert(1 == 1, "1 should equal 1")

    @pytest.mark.title("Soft assert xfail test without Markers")
    def test_soft_assert_xfail(self) -> None:
        """Test demonstrating expected failure in soft assertion."""
        pytest.xfail("Expected failure for demonstration purposes")
        soft_assert(1 == 2, "1 should equal 2")
