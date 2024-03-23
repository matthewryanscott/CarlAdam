from __future__ import annotations

from itertools import islice
from typing import FrozenSet, Iterator, Mapping, MutableMapping, Protocol, Sequence, TYPE_CHECKING, Tuple

from attr import define
from pyrsistent import pmap

from carladam.petrinet import defaults

if TYPE_CHECKING:  # pragma: nocover
    from carladam.petrinet.token import Token, TokenSet
    from carladam.petrinet.transition import TransitionFunction


@define
class Color:
    """A `Color` is a discrete label used to differentiate types of `Token`s."""

    label: str
    "Globally unique name of this `Color`."

    def __repr__(self):
        return self.label

    def __hash__(self):
        """Colors with the same name are the same color."""
        return hash(self.label)

    def __call__(self, **kwargs) -> Token:
        """Return a `Token` of this `Color`, having its `data` set to the passed-in `kwargs`."""
        from carladam.petrinet.token import Token

        return Token(color=self, data=kwargs)

    def passthrough(self, quantity: int = 1) -> TransitionFunction:
        """Return a transition function that passes through (unmodified) tokens of this color."""
        from carladam.petrinet.transition import passthrough

        return passthrough({self: quantity})

    def token_generator(self, data: Mapping) -> Iterator[Token]:
        """Return a generator that produces tokens of this color with the given `data`."""
        from carladam.petrinet.token import Token

        data = pmap(data)
        while True:
            yield Token(color=self, data=data)

    def produce(self, quantity: int = 1, **kwargs) -> TransitionFunction:
        """Return a transition function that generates a given quantity of this color of token."""

        def transition_fn(inputs: TokenSet) -> Iterator[TokenSet]:
            yield frozenset(islice(self.token_generator(kwargs), quantity))

        return transition_fn


class HasColor(Protocol):
    color: Color


Abstract = Color(defaults.ABSTRACT_TOKEN)
"Abstract tokens are indicated by a filled circle."

Quantity = int
ColorSet = Mapping[Color, Quantity]
"""Mapping between a set of `Color`s and an expected quantity of tokens of that color.

These are used to specify

These are also used when transforming a `Marking` (mapping of `Place` → `Set[Token]`)
into a mapping of `Place` → (`Color` → `Quantity`).
"""

MutableColorSet = MutableMapping[Color, Quantity]
"""Pyrsistent version of ColorSet."""

ColorSetItem = Tuple[Color, Quantity]
"A single item in a ColorSet."

FrozenColorSet = FrozenSet[ColorSetItem]
"A frozenset transformation of a ColorSet."


def colorset_string(colorset: ColorSet) -> str:
    """Return a string representation of a `ColorSet` suitable for decorating an `Arc` in a diagram."""
    if colorset == {Abstract: 1}:
        return ""
    sorted_colorset: Sequence[tuple[str, Quantity]] = sorted(
        (color.label, quantity) for color, quantity in colorset.items()
    )
    return "".join(name * quantity for name, quantity in sorted_colorset)


def color_eq(color: Color):
    """Return a function that compares an object's `color` property with the given `color`."""

    def comparator(obj: HasColor):
        return obj.color == color

    return comparator
