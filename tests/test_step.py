from time import sleep
import pytest

from sdk_pytest_checkmate import soft_assert, step


@pytest.mark.epic("Step")
class TestStep:
    @pytest.mark.title("Step function test")
    def test_step_function(self):
        step("Description for step 1")
        soft_assert(1 == 1, "1 should equal 1")
        step("Description for step 2")
        soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Step context manager test")
    def test_step_context(self):
        with step("Description for step 1"):
            sleep(0.2)
            soft_assert(1 == 1, "1 should equal 1")
        with step("Description for step 2"):
            soft_assert(2 == 2, "2 should equal 2")

    @pytest.mark.title("Step with soft_assert")
    def test_step_with_soft_assert(self):
        with step("Description for step 1"):
            soft_assert(1 == 1, "1 should equal 1")
        with step("Description for step 2"):
            sleep(0.2)
            soft_assert(2 == 2, "2 should equal 2")
            soft_assert(3 == 3, "3 should equal 3")
        with step("Description for step 3"):
            sleep(0.2)
            soft_assert(4 == 4, "4 should equal 4")
            soft_assert(5 == 5, "5 should equal 5")
