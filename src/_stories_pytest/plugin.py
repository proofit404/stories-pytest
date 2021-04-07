import linecache
import sys
import textwrap

import _pytest.config
import _stories.context
import _stories.mounted

from _stories_pytest.exceptions import StoryPytestError


origin_make_context = _stories.context.make_context


def _track_context(storage):
    def wrapper(contract, kwargs, history):
        ctx, ns, lines, bind = origin_make_context(contract, kwargs, history)
        storage.append((_get_test_source(*_get_test_call()), history, ns, lines))
        return ctx, ns, lines, bind

    return wrapper


def _get_test_call():
    f = sys._getframe()
    return _search_test_frame(f)


def _search_test_frame(f):
    while True:
        if _is_inside_test_function(f):
            return f.f_code.co_filename, f.f_lineno
        elif not f.f_back:
            raise StoryPytestError("Can not find running test")
        else:
            f = f.f_back


def _is_inside_test_function(f):
    return "@pytest_ar" in f.f_globals and f.f_code.co_filename != __file__


def _get_test_source(filename, lineno):

    start = max(1, lineno - 3)
    end = lineno + 4
    adjust_to = len(str(end - 1))

    lines = [linecache.getline(filename, no) for no in range(start, end)]
    text = textwrap.dedent("".join(lines))

    src = []
    for num, line in zip(range(start, end), text.splitlines()):
        sep = "->" if num == lineno else "  "
        src.append((" {} {} {}".format(str(num).rjust(adjust_to), sep, line)).rstrip())

    src = "\n".join(src)

    return src


@_pytest.config.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Report stories executed during the test."""
    storage = []
    _stories.mounted.make_context = _track_context(storage)
    yield
    _stories.mounted.make_context = origin_make_context
    for i, (src, history, ns, lines) in enumerate(storage, 1):
        output = "\n\n".join(
            [
                src,
                _stories.context.history_representation(history)
                + "\n\n"
                + _stories.context.context_representation(ns, lines),
            ]
        )
        item.add_report_section("call", "story #%d" % (i,), output)
