"""Tests related to stories_pytest module."""
from operator import attrgetter

import pytest

from _stories_pytest.plugin import _search_test_frame
from stories_pytest.exceptions import StoryPytestError


@pytest.mark.parametrize(
    "run", [attrgetter("runpytest_inprocess"), attrgetter("runpytest_subprocess")]
)
def test_passed_no_stories(pytester, pytestargs, run):
    """Section should not be displayed for passed test without stories executed."""
    pytester.makepyfile(
        """
from examples import simple_view

def test_passed():
    simple_view()
    assert True
""".lstrip()
    )
    result = run(pytester)(*pytestargs)
    result.assert_outcomes(passed=1)
    assert "Captured story" not in str(result.stdout)


@pytest.mark.parametrize(
    "run", [attrgetter("runpytest_inprocess"), attrgetter("runpytest_subprocess")]
)
def test_failed_no_stories(pytester, pytestargs, run):
    """Section should not be displayed for failed test without stories executed."""
    pytester.makepyfile(
        """
from examples import simple_view

def test_fail():
    simple_view()
    assert False
""".lstrip()
    )
    result = run(pytester)(*pytestargs)
    result.assert_outcomes(failed=1)
    assert "Captured story" not in str(result.stdout)


@pytest.mark.parametrize(
    "run", [attrgetter("runpytest_inprocess"), attrgetter("runpytest_subprocess")]
)
def test_passed_stories_executed(pytester, pytestargs, run):
    """Section should not be displayed for passed test with stories executed."""
    pytester.makepyfile(
        """
from examples import story_view

def test_passed():
    story_view()
    assert True
""".lstrip()
    )
    result = run(pytester)(*pytestargs)
    result.assert_outcomes(passed=1)
    assert "Captured story" not in str(result.stdout)


@pytest.mark.parametrize(
    ("run", "first_source", "second_source"),
    [
        (attrgetter("runpytest_inprocess"), "", ""),
        (
            attrgetter("runpytest_subprocess"),
            (
                "",
                "from examples import story_view",
                "",
                "def test_fail():",
                "    story_view()",
                "    admin_view()",
                "    assert False",
                "",
            ),
            (
                "",
                "",
                "def test_fail():",
                "    story_view()",
                "    admin_view()",
                "    assert False",
                "",
                "# A comment.",
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    ("prefix", "suffix", "first_margin", "second_margin"),
    [
        (
            "",
            "",
            (
                "---",
                " 2    ",
                " 3",
                " 4    ",
                " 5 -> ",
                " 6    ",
                " 7    ",
                " 8",
            ),
            (
                "---",
                " 3",
                " 4    ",
                " 5    ",
                " 6 -> ",
                " 7    ",
                " 8",
                " 9    ",
            ),
        ),
        (
            "...\n\n",
            "\n\n\n...",
            (
                "---",
                "  4    ",
                "  5",
                "  6    ",
                "  7 -> ",
                "  8    ",
                "  9    ",
                " 10",
            ),
            (
                "---",
                "  5",
                "  6    ",
                "  7    ",
                "  8 -> ",
                "  9    ",
                " 10",
                " 11    ",
            ),
        ),
    ],
)
def test_failed_stories_executed(
    pytester,
    pytestargs,
    run,
    first_source,
    second_source,
    prefix,
    suffix,
    first_margin,
    second_margin,
):
    """Section should be displayed for failed test with stories executed."""
    pytester.makepyfile(
        f"""{prefix}from examples import admin_view
from examples import story_view

def test_fail():
    story_view()
    admin_view()
    assert False

# A comment.{suffix}
"""
    )
    result = run(pytester)(*pytestargs)
    result.assert_outcomes(failed=1)
    assert "Captured story #1 call" in str(result.stdout)

    first_output = "\n".join(
        margin + source for margin, source in zip(first_margin, first_source)
    )

    expected = f"""
{first_output}

Action.do
  one
  two
  three (returned: 5)

Context:
  bar: 2     # Story argument
  foo: 1     # Story argument
  baz: 3     # Set by Action.one
  quiz: 6    # Set by Action.two
  result: 5  # Set by Action.three
    """.strip()

    assert expected in str(result.stdout)

    assert "Captured story #2 call" in str(result.stdout)

    second_output = "\n".join(
        margin + source for margin, source in zip(second_margin, second_source)
    )

    expected = f"""
{second_output}

Admin.do
  x
  y
  z (errored: AdminError)

Context()
    """.strip()

    assert expected in str(result.stdout)


def test_failed_stories_executed_short_test(pytester, pytestargs):
    """Some test files could be very short.

    We should be able to handle display calling frame in that case.

    """
    pytester.makepyfile(
        """
from examples import story_view
def test_fail():
    story_view()
    assert False
""".lstrip()
    )
    result = pytester.runpytest_subprocess(*pytestargs)
    result.assert_outcomes(failed=1)
    assert "Captured story #1 call" in str(result.stdout)

    expected = """
 1    from examples import story_view
 2    def test_fail():
 3 ->     story_view()
 4        assert False

Action.do
  one
  two
  three (returned: 5)

Context:
  bar: 2     # Story argument
  foo: 1     # Story argument
  baz: 3     # Set by Action.one
  quiz: 6    # Set by Action.two
  result: 5  # Set by Action.three
    """.strip()

    assert expected in str(result.stdout)


def test_deactivate_instrumentation(pytester, pytestargs):
    """Story should be kept in a working state after test run."""
    pytester.makepyfile(
        """
import atexit

from examples import story_view

def test_passed():
    story_view()
    assert True

def handler():
    try:
        story_view()
    except Exception:  # noqa: B902
        raise HandledError("Stories are broken")

class HandledError(Exception):
    pass

atexit.register(handler)
""".lstrip()
    )
    result = pytester.runpytest_subprocess(*pytestargs)
    result.assert_outcomes(passed=1)
    assert "HandledError: Stories are broken" not in str(result.stderr)


def test_caller_frame_not_found():
    """Raise exception in case we could not identify execution context."""

    class Frame:
        f_globals = {}
        f_back = None

    with pytest.raises(StoryPytestError) as exc_info:
        _search_test_frame(Frame())

    assert str(exc_info.value) == "Can not find running test"
