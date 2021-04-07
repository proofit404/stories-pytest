from examples.exceptions import AdminError
from examples.services import Action
from examples.services import Admin


def simple_view():
    """Do stuff."""
    pass


def story_view():
    """Do stuff using story."""
    action = Action()
    action.do(foo=1, bar=2)


def admin_view():
    """Do stuff using story."""
    action = Admin()
    try:
        action.do()
    except AdminError:
        pass
