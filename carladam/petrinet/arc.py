"""
An Arc is a directed connection from `Place` → `Transition` or `Transition` → `Place`.

Note: The classes in this module contain a lot of duplication.
These will be cleaned up in a future effort that will remove the use of `attrs` which is subclass-unfriendly.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import AbstractSet, Callable, Iterator, TYPE_CHECKING, overload

from attr import Factory, define, field
from attr.validators import instance_of, optional
from pyrsistent import pmap

from carladam.petrinet import defaults, errors
from carladam.petrinet.color import Abstract, Color, ColorSet, colorset_string
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token, TokenSet
from carladam.petrinet.transition import Transition

if TYPE_CHECKING:  # pragma: nocover
    from carladam.petrinet.types import Arc


@overload
def arc(
    src: Place,
    dest: Transition,
    weight: Color | ColorSet = None,
    *,
    annotation: str = None,
    transform: Callable = None,
    guard: Callable = None,
) -> CompletedArcPT: ...


@overload
def arc(
    src: Transition,
    dest: Place,
    weight: Color | ColorSet = None,
    *,
    annotation: str = None,
    transform: Callable = None,
    guard: Callable = None,
) -> CompletedArcTP: ...


def arc(src, dest, weight=None, **kwargs):
    if isinstance(weight, Color):
        weight = {weight: 1}
    elif weight is None:
        weight = {Abstract: 1}
    if isinstance(src, Place) and isinstance(dest, Transition):
        return CompletedArcPT(src, dest, weight, **kwargs)
    if isinstance(src, Transition) and isinstance(dest, Place):
        return CompletedArcTP(src, dest, weight, **kwargs)
    raise TypeError("Arcs must be from Place to Transition or Transition to Place.")


def __arc_hash__(self):
    """Common implementation of `__hash__` for all Arc types."""
    return hash((self.src, self.dest, frozenset(self.weight.items())))


def __arc_lt__(self, other):
    """Common implementation of `__lt__` for all Arc types."""
    return (self.src.name, self.dest.name) < (other.src.name, other.dest.name)


def __arc_repr__(self: Arc):
    """Common implementation of `__repr__` for all Arc types."""
    annotation = f" {self.annotation}" if self.annotation else ""
    colorset = f" {s}" if (s := colorset_string(self.weight)) else ""
    return f"{self.src!r}{colorset}{annotation} {defaults.ARROW} {self.dest!r}"


@lru_cache
def default_arc_weight() -> ColorSet:
    """By default, arcs transmit a single Abtract token."""
    return pmap({Abstract: 1})


def weights_are_satisfied(arc: CompletedArcPT, tokens: AbstractSet[Token]) -> bool:
    colors: ColorSet = Counter(token.color for token in tokens)
    # Do the tokens have all the colors specified by the arc weight?
    if frozenset(arc.weight) - frozenset(colors):
        return False
    # Do the tokens satisfy all of the quantities specified by the arc weight?
    return all(arc.weight[color] <= count for color, count in colors.items())


@define
class ArcPT:
    """An arc from `Place` → `Transition`."""

    src: Place | None = field(default=None, validator=optional(instance_of(Place)))
    """The place where the transition will consume token(s) from."""

    dest: Transition | None = field(default=None, validator=optional(instance_of(Transition)))
    """The transition that will consume token(s) from the place."""

    weight: ColorSet = Factory(default_arc_weight)
    """The type and amount of tokens that will be consumed."""

    annotation: str | None = None
    """Human-friendly annotation to display with this arc when representing it."""

    # noinspection PyUnresolvedReferences
    transform: Callable | None = None
    """Function that will transform each token consumed."""

    guard: Callable = weights_are_satisfied
    """Function that returns True if the input tokens pass criteria."""

    completed: bool = False
    """Whether this arc has both a src and dest given."""

    def __lshift__(self, other: Place | Annotate | TransformEach) -> ArcPT:
        if isinstance(other, (Annotate, TransformEach)):
            return other.apply_to_arc(self)
        if self.dest is None:
            raise errors.PetriNetArcIncomplete("Cannot << to an arc not having a dest")
        return CompletedArcPT(
            src=other,
            dest=self.dest,
            weight=self.weight,  # type: ignore
            annotation=self.annotation,
            transform=self.transform,
        )

    def __rshift__(self, other: Transition | Annotate | TransformEach) -> ArcPT:
        if isinstance(other, (Annotate, TransformEach)):
            return other.apply_to_arc(self)
        if self.src is None:
            raise errors.PetriNetArcIncomplete("Cannot >> from an arc not having a src")
        return CompletedArcPT(
            src=self.src,
            dest=other,
            weight=self.weight,  # type: ignore
            annotation=self.annotation,
            transform=self.transform,
        )

    def __call__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self


@define
class CompletedArcPT(ArcPT):
    """A completely-specified ArcPT."""

    src: Place = field(validator=instance_of(Place))
    dest: Transition = field(validator=instance_of(Transition))
    weight: ColorSet = Factory(default_arc_weight)
    annotation: str | None = None
    # noinspection PyUnresolvedReferences
    transform: Callable | None = None
    guard: Callable = weights_are_satisfied
    completed: bool = True

    __hash__ = __arc_hash__
    __lt__ = __arc_lt__
    __repr__ = __arc_repr__


@define
class ArcTP:
    """An arc from `Transition` → `Place`."""

    src: Transition | None = field(default=None, validator=optional(instance_of(Transition)))
    """The transition that will produce token(s) to the place."""

    dest: Place | None = field(default=None, validator=optional(instance_of(Place)))
    """The place where the transition will produce token(s) to."""

    weight: ColorSet = field(factory=default_arc_weight, converter=pmap)
    """The type and amount of tokens that will be consumed."""

    annotation: str | None = None
    """Human-friendly annotation to display with this arc when representing it."""

    # noinspection PyUnresolvedReferences
    transform: Callable | None = None
    """Function that will transform each token consumed."""

    completed: bool = False
    """Whether this arc has both a src and dest given."""

    def __lshift__(self, other: Transition | Annotate | TransformEach) -> ArcTP:
        if isinstance(other, (Annotate, TransformEach)):
            return other.apply_to_arc(self)
        if self.dest is None:
            raise errors.PetriNetArcIncomplete("Cannot << to an arc not having a dest")
        return CompletedArcTP(
            src=other,
            dest=self.dest,
            weight=self.weight,  # type: ignore
            annotation=self.annotation,
            transform=self.transform,
        )

    def __rshift__(self, other: Place | Annotate | TransformEach) -> ArcTP:
        if isinstance(other, (Annotate, TransformEach)):
            return other.apply_to_arc(self)
        if self.src is None:
            raise errors.PetriNetArcIncomplete("Cannot >> from an arc not having a src")
        return CompletedArcTP(
            src=self.src,
            dest=other,
            weight=self.weight,  # type: ignore
            annotation=self.annotation,
            transform=self.transform,
        )


@define
class CompletedArcTP(ArcTP):
    """A completely-specified ArcTP."""

    src: Transition = field(validator=instance_of(Transition))
    dest: Place = field(validator=instance_of(Place))
    weight: ColorSet = field(factory=default_arc_weight, converter=pmap)
    annotation: str | None = None
    # noinspection PyUnresolvedReferences
    transform: Callable | None = None
    completed: bool = True

    __hash__ = __arc_hash__
    __lt__ = __arc_lt__
    __repr__ = __arc_repr__


@define
class Annotate:
    """Decorates an `Arc` with descriptive text to show in diagrams."""

    text: str
    "Text used to describe an `Arc`."

    @overload
    def apply_to_arc(self, arc: ArcPT) -> ArcPT: ...

    @overload
    def apply_to_arc(self, arc: ArcTP) -> ArcTP: ...

    def apply_to_arc(self, arc: Arc) -> Arc:
        return type(arc)(
            src=arc.src,  # type: ignore
            dest=arc.dest,  # type: ignore
            weight=arc.weight,  # type: ignore
            annotation=self.text,
            transform=arc.transform,
        )


@define
class TransformEach:
    """Sets a function on an `Arc` that transforms each `Token` passing through it during a `Transition`."""

    fn: Callable
    "Function taking a `Token` and returning a `Token`."

    @overload
    def apply_to_arc(self, arc: ArcPT) -> ArcPT: ...

    @overload
    def apply_to_arc(self, arc: ArcTP) -> ArcTP: ...

    def apply_to_arc(self, arc: Arc) -> Arc:
        def transformed_tokens(tokens: TokenSet) -> Iterator[Token]:
            for token in tokens:
                yield self.fn(token)

        def transform(tokens: TokenSet) -> TokenSet:
            return frozenset(transformed_tokens(tokens))

        return type(arc)(
            src=arc.src,  # type: ignore
            dest=arc.dest,  # type: ignore
            weight=arc.weight,  # type: ignore
            annotation=arc.annotation,
            transform=transform,
        )
