from stories import arguments
from stories import Result
from stories import story
from stories import Success

from examples.exceptions import AdminError


class Action:
    """Service."""

    @story
    @arguments("foo", "bar")
    def do(I):
        """Define service."""
        I.one
        I.two
        I.three

    def one(self, state):
        """Do step."""
        state.baz = state.foo + state.bar
        return Success()

    def two(self, state):
        """Do step."""
        state.quiz = state.baz * 2
        return Success()

    def three(self, state):
        """Do step."""
        state.result = state.quiz - 1
        return Result(state.result)


class Admin:
    """Service."""

    @story
    def do(I):
        """Define service."""
        I.x
        I.y
        I.z

    def x(self, state):
        """Do step."""
        return Success()

    def y(self, state):
        """Do step."""
        return Success()

    def z(self, state):
        """Do step."""
        raise AdminError
