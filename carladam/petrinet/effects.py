from __future__ import annotations

from typing import Sequence

import attrs
from pyrsistent import pset

from carladam.petrinet.arc import CompletedArcPT, CompletedArcTP
from carladam.petrinet.marking import PMarking
from carladam.petrinet.token import Token


@attrs.define
class Consume:
    """
    A token was consumed from a place by an arc.

    The token will always represent a token that was present in a place prior to a transition occurrence.
    """

    arc: CompletedArcPT
    token: Token

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        new_place_tokens = marking.get(self.arc.src, pset()).remove(self.token)
        if new_place_tokens:
            return marking.set(self.arc.src, pset(new_place_tokens))
        return marking.remove(self.arc.src)


@attrs.define
class Input:
    """
    A token was passed to a transition as an input.

    The token may be one that was consumed from a place, or one that was generated by an arc's `transform` function.
    """

    arc: CompletedArcPT
    token: Token

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        return marking


@attrs.define
class Output:
    """
    A token was returned by a transition as an output.

    The token will always represent a token that was generated by the transition's `fn` function.
    """

    arc: CompletedArcTP
    token: Token

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        return marking


@attrs.define
class Produce:
    """
    A token was produced to a place by an arc.

    The token may be one that was generated by a transition's `fn` function,
    or it may be one that was generated by an arc's `transform` function.
    """

    arc: CompletedArcTP
    token: Token

    def apply_to_marking(self, marking: PMarking) -> PMarking:
        new_place_tokens = marking.get(self.arc.dest, pset()).add(self.token)
        return marking.set(self.arc.dest, pset(new_place_tokens))


Effect = Consume | Input | Output | Produce


def apply_effects_to_marking(marking: PMarking, effects: Sequence[Effect]) -> PMarking:
    for effect in effects:
        marking = effect.apply_to_marking(marking)
    return marking
