from __future__ import annotations

# Python imports
from typing import AbstractSet, TYPE_CHECKING, overload

# Pip imports
from attr import define, field
from pyrsistent import PMap, PSet

# Internal imports
from carladam.petrinet import defaults
from carladam.petrinet.color import Color, ColorSet
from carladam.petrinet.defaults import default_id

if TYPE_CHECKING:  # pragma: nocover
    # Internal imports
    from carladam.petrinet.arc import ArcPT, ArcTP, CompletedArcPT
    from carladam.petrinet.transition import Transition


@define
class Place:
    """A `Place` represents where `Token`s can be mapped to via a `Marking` of a `PetriNet`."""

    id: str = field(factory=default_id, repr=False)
    "Globally unique ID, used as a hash key."

    name: str = field()
    "Descriptive name, usually but not necessarily unique within a net."

    icon: str | None = defaults.PLACE
    "Icon/emoji to use when decorating this transition visually."

    # noinspection PyUnresolvedReferences
    @name.default
    def _default_name_is_id(self):
        """By default, `name` is set to the `id` if not passed in."""
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        """Places are sorted by name."""
        return self.name < other.name

    def __repr__(self):
        if self.icon:
            return f"{self.icon} {self.name}"
        if self.name != self.id:
            return self.name
        return f"<Place id={self.id!r}>"

    def __lshift__(self, other: Transition | Color | ColorSet | AbstractSet[Color]) -> ArcTP:
        """Returns an arc from this `Place` from the given `Transition`."""
        # Internal imports
        from carladam.petrinet.arc import ArcTP, CompletedArcTP
        from carladam.petrinet.transition import Transition

        if isinstance(other, Color):
            other = {other: 1}
        if isinstance(other, (set, frozenset, PSet)):
            other = {color: 1 for color in other}
        if isinstance(other, (dict, PMap)):
            return ArcTP(src=None, dest=self, weight=other)

        if isinstance(other, Transition):
            return CompletedArcTP(src=other, dest=self)

        raise TypeError("Place cannot be connected to object.", other)

    @overload
    def __rshift__(self, other: Transition) -> CompletedArcPT: ...

    @overload
    def __rshift__(self, other: Color | ColorSet | AbstractSet[Color]) -> ArcPT: ...

    def __rshift__(self, other: Transition | Color | ColorSet | AbstractSet[Color]) -> ArcPT | CompletedArcPT:
        """Returns an arc from this `Place` to the given `Transition`."""
        # Internal imports
        from carladam.petrinet.arc import ArcPT, CompletedArcPT
        from carladam.petrinet.transition import Transition

        if isinstance(other, Color):
            other = {other: 1}
        if isinstance(other, (set, frozenset, PSet)):
            other = {color: 1 for color in other}
        if isinstance(other, (dict, PMap)):
            return ArcPT(src=self, dest=None, weight=other)

        if isinstance(other, Transition):
            return CompletedArcPT(src=self, dest=other)

        raise TypeError("Place cannot be connected to object.", other)
