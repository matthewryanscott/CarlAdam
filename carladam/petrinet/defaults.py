# Python imports
from uuid import uuid4


def default_id() -> str:
    """Returns a random unique UUID string."""
    return uuid4().hex


TRANSITION = "□"
"""Decoration for Transition instances."""

PLACE = "⬭"
"""Decoration for Place instances."""

ARROW = "→"
"""Arrow decoration for Arc instances."""

EMPTY_SET = "∅"
"""Decorative representation of empty set."""

ABSTRACT_TOKEN = "⚫️"
"""Color name given to abstract tokens."""
