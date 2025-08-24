import pytest

from sdk_pytest_checkmate import soft_assert


@pytest.mark.epic("Soft Assert")
@pytest.mark.story("Soft Assert Story")
class TestSoftAssert:
    @pytest.mark.title("Soft assert passed test with Markers")
    def test_soft_assert_markers_passed(self):
        soft_assert(1 == 1, "1 should equal 1")
        soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Soft assert failed test with Markers")
    def test_soft_assert_markers_failed(self):
        soft_assert(1 == 2, "1 should equal 2")
        soft_assert(2 == 3, "2 should equal 3")

    @pytest.mark.title("Soft assert mixed test with Markers")
    def test_soft_assert_markers_mixed(self):
        soft_assert(1 == 1, "1 should equal 1")
        soft_assert(2 == 3, "2 should equal 3")
        soft_assert(2 == 2, "2 should equal 2")
        soft_assert(3 == 4, "3 should equal 4")


@pytest.mark.epic("Soft Assert")
@pytest.mark.story("Soft Assert Story")
@pytest.mark.title("Soft assert skip test without Markers")
def test_soft_assert_skip():
    pytest.skip("Skipping this test for demonstration purposes")
    soft_assert(1 == 1, "1 should equal 1")
