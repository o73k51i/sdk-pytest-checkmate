import pytest


def test_passed():
    assert True


def test_failed():
    assert False, "This test is designed to fail"


@pytest.mark.skip(reason="Skipping this test for demonstration purposes")
def test_skip():
    pass


@pytest.mark.xfail(reason="Expected failure for demonstration purposes")
def test_expected_failure():
    assert False, "This test is expected to fail"
