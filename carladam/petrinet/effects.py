from __future__ import annotations

import typing
from typing import Sequence

import attrs
from pyrsistent import pset

from carladam.petrinet.arc import CompletedArcPT, CompletedArcTP
from carladam.petrinet.marking import PMarking
from carladam.petrinet.token import Token

if typing.TYPE_CHECKING:
    pass


@attrs.define
class Consume:
    """A token was consumed from a place by an arc."""

    arc: CompletedArcPT
    token: Token

    def __hash__(self):
        return hash((Consume, self.arc, self.token))

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        new_place_tokens = marking.get(self.arc.src, pset()).remove(self.token)
        return marking.set(self.arc.src, pset(new_place_tokens))


@attrs.define
class Input:
    """A token was passed to a transition as an input."""

    arc: CompletedArcPT
    token: Token

    def __hash__(self):
        return hash((Input, self.arc, self.token))

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        return marking


@attrs.define
class Output:
    """A token was returned by a transition as an output."""

    arc: CompletedArcTP
    token: Token

    def __hash__(self):
        return hash((Output, self.arc, self.token))

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        return marking


@attrs.define
class Produce:
    """A token was produced to a place by an arc."""

    arc: CompletedArcTP
    token: Token

    def __hash__(self):
        return hash((Produce, self.arc, self.token))

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        new_place_tokens = marking.get(self.arc.dest, pset()).add(self.token)
        return marking.set(self.arc.dest, pset(new_place_tokens))


Effect = Consume | Input | Output | Produce


def apply_effects_to_marking(marking: PMarking, effects: Sequence[Effect]) -> PMarking:
    for effect in effects:
        marking = effect.apply_to_marking(marking)
    return marking
