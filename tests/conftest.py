"""Settings module for the Py.test tool."""
import pkg_resources
import pytest


pytest_plugins = ["examples", "pytester"]


@pytest.fixture()
def pytestargs():
    """Prepare arguments for pytest subprocess."""
    try:
        pkg_resources.get_distribution("stories_pytest")
    except pkg_resources.DistributionNotFound:  # pragma: no cover
        return ["-p", "stories_pytest"]
    else:
        return []
