import pytest


@pytest.mark.title("Title marker DEMO")
def test_marker_title():
    pass


@pytest.mark.epic("Epic marker DEMO")
def test_marker_epic():
    pass


@pytest.mark.story("Story marker DEMO")
def test_marker_story():
    pass


@pytest.mark.epic("Demo Epic")
@pytest.mark.story("Demo Story")
@pytest.mark.title("Demo Test with Markers")
def test_markers_passed():
    assert True


@pytest.mark.epic("Demo Epic")
@pytest.mark.story("Demo Story")
@pytest.mark.title("Demo Test with Markers")
def test_markers_failed():
    assert False