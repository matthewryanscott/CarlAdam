from __future__ import annotations

# Python imports
from collections import Counter, defaultdict
from collections.abc import Iterable
from typing import AbstractSet, Callable, Iterator, TYPE_CHECKING, cast, overload

# Pip imports
from attr import define, field
from pyrsistent import PMap, PSet, pmap, pset

# Internal imports
from carladam.petrinet import defaults
from carladam.petrinet.color import Abstract, Color, ColorSet, MutableColorSet
from carladam.petrinet.defaults import default_id
from carladam.petrinet.token import TokenSet

if TYPE_CHECKING:  # pragma: nocover
    # Internal imports
    from carladam.petrinet.arc import ArcPT, ArcTP, CompletedArcTP
    from carladam.petrinet.place import Place

TransitionGuard = Callable[[TokenSet], bool]
"Type of function receiving a set of `Token`s from input `Place`s and returning `True` if guard(s) are met."

TransitionFunction = Callable[[TokenSet], Iterator[TokenSet]]


def always(value: bool) -> TransitionGuard:
    """Returns a transition guard function that always returns `value`."""

    def transition_guard(inputs: TokenSet) -> bool:
        return value

    return transition_guard


def convert_fn_list_to_generator(fn: Iterator[TransitionFunction] | TransitionFunction) -> TransitionFunction:
    """Given a list of functions, return a generator that yields the results of calling each function."""
    if not isinstance(fn, Iterable):
        return fn

    def _fn(inputs: TokenSet) -> Iterator[TokenSet]:
        for inner_fn in cast(Iterator[TransitionFunction], fn):
            yield from inner_fn(inputs)

    return _fn


def passthrough(*colorsets: Color | ColorSet | AbstractSet) -> TransitionFunction:
    """
    Return a transition function that passes through inputs as outputs, optionally matching a colorset.

    The colorset used for matching is the superset of the colorsets passed in.
    """

    def _fn_all(inputs: TokenSet) -> Iterator[TokenSet]:
        yield pset(inputs)

    if not colorsets:
        return _fn_all

    passthrough_colorset_dict: MutableColorSet = defaultdict(int)
    for colorset in colorsets:
        if colorset and isinstance(colorset, Color):
            colorset = {colorset: 1}
        if colorset and isinstance(colorset, (set, frozenset, PSet)):
            colorset = {color: 1 for color in colorset}
        if not isinstance(colorset, (dict, PMap)):
            continue
        color: Color
        quantity: int
        for color, quantity in colorset.items():
            passthrough_colorset_dict[color] += quantity
    passthrough_colorset = pmap(passthrough_colorset_dict)

    def _fn(inputs: TokenSet) -> Iterator[TokenSet]:
        inputs_colorset = pmap(Counter(token.color for token in inputs))
        if inputs_colorset == passthrough_colorset:
            # Direct match.
            yield pset(inputs)
            return
        # Pass through a subset if we can.
        # Note: Token selection order is undefined if len of input tokens of a certain color
        # exceeds the corresponding colorset quantity.
        remaining = dict(passthrough_colorset)
        subset = set()
        for token in inputs:
            if token.color not in remaining:
                continue
            subset.add(token)
            remaining[token.color] -= 1
            if not remaining[token.color]:
                del remaining[token.color]
        if remaining:
            return
        yield pset(subset)

    return _fn


@define
class Transition:
    """When a `Transition` occurs it consumes `Token`s from `Place`s and produces `Token`s to `Place`s."""

    id: str = field(factory=default_id, repr=False)
    "Globally unique ID, used as a hash key."

    name: str = field()
    "Descriptive name, usually but not necessarily unique within a net."

    guard: TransitionGuard = field(default=always(True))
    "Function accepting a set of `Token`s and returning True if guard conditions are met."

    annotation: str | None = None
    "Text annotation to show on a diagram."

    fn: TransitionFunction = field(
        default=Abstract.produce(),
        repr=False,
        converter=convert_fn_list_to_generator,
    )
    "Function accepting a set of `Token`s to consume and returning a sequence of `TokenSet` generators."

    icon: str = defaults.TRANSITION
    "Icon/emoji to use when decorating this transition visually."

    # noinspection PyUnresolvedReferences
    @name.default
    def _default_name_is_id(self):
        """By default, `name` is set to the `id` if not passed in."""
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        """Transitions are sorted by name."""
        return self.name < other.name

    def __repr__(self):
        if self.icon:
            return f"{self.icon} {self.name}"
        if self.name != self.id:
            return self.name
        return f"<Transition id={self.id!r}>"

    def __lshift__(self, other: Place | Color | ColorSet | AbstractSet[Color]) -> ArcPT:
        """Returns an arc from this `Transition` from the given `Place`."""
        # Internal imports
        from carladam.petrinet.arc import ArcPT, CompletedArcPT
        from carladam.petrinet.place import Place

        if isinstance(other, Color):
            other = {other: 1}
        if isinstance(other, (set, frozenset, PSet)):
            other = {color: 1 for color in other}
        if isinstance(other, dict):
            return ArcPT(src=None, dest=self, weight=other)
        if isinstance(other, Place):
            return CompletedArcPT(src=other, dest=self)
        raise TypeError("Transition cannot be connected to object.", other)

    @overload
    def __rshift__(self, other: Place) -> CompletedArcTP: ...

    @overload
    def __rshift__(self, other: Color | ColorSet | AbstractSet[Color]) -> ArcTP: ...

    def __rshift__(self, other: Place | Color | ColorSet | AbstractSet[Color]) -> ArcTP | CompletedArcTP:
        """Returns an arc from this `Transition` to the given `Place`."""
        # Internal imports
        from carladam.petrinet.arc import ArcTP, CompletedArcTP
        from carladam.petrinet.place import Place

        if isinstance(other, Color):
            other = {other: 1}
        if isinstance(other, (set, frozenset, PSet)):
            other = {color: 1 for color in other}
        if isinstance(other, dict):
            return ArcTP(src=self, dest=None, weight=other)
        if isinstance(other, Place):
            return CompletedArcTP(src=self, dest=other)
        raise TypeError("Transition cannot be connected to object.", other)
