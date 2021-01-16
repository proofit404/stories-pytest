"""Tests related to stories_pytest module."""
from stories_pytest.exceptions import StoryPytestError


def test_exception():
    """`StoryPytestError` should be Exception subclass."""
    assert issubclass(StoryPytestError, Exception)
