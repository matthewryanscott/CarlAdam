from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence, TYPE_CHECKING

import attrs
from pyrsistent import plist, pmap, pset
from pyrsistent.typing import PList

from carladam.petrinet.arc import CompletedArcPT, CompletedArcTP
from carladam.petrinet.color import ColorSet
from carladam.petrinet.effects import Consume, Effect, Input, Output, Produce
from carladam.petrinet.errors import (
    ArcGuardRaisesException,
    ArcGuardReturnsFalse,
    PetriNetTransitionFunctionOutputHasOverlappingColorsets,
    TransitionGuardRaisesException,
    TransitionGuardReturnsFalse,
    TransitionHasNoArcs,
    TransitionNotEnabled,
)
from carladam.petrinet.marking import PMarking
from carladam.petrinet.token import TokenSet
from carladam.petrinet.transition import Transition

if TYPE_CHECKING:
    from carladam.petrinet.petrinet import PetriNet  # pragma: nocover


@attrs.define
class Occurrence:
    net: PetriNet
    marking: PMarking
    transition: Transition

    def is_enabled(self) -> bool:
        try:
            self.check_enabled()
        except TransitionNotEnabled:
            return False
        return True

    def check_enabled(self):
        self._check_transition_connectivity()
        for arc in self.input_arcs():
            tokens = self.marking.get(arc.src, set())
            self._check_arc_guard(arc, tokens)
        self._check_transition_guard()

    def _check_transition_connectivity(self):
        """Checks that the transition is connected to at least one arc."""
        input_arcs = self.net.node_inputs.get(self.transition)
        output_arcs = self.net.node_outputs.get(self.transition)
        if not input_arcs and not output_arcs:
            raise TransitionHasNoArcs()

    def _check_arc_guard(self, arc, tokens):
        """
        Checks that the arc guard passes.

        [NOTE]: This checks tokens that will be consumed from a place,
         *before* an arc's `transform` method is called.
         See also https://github.com/matthewryanscott/CarlAdam/issues/14
        """
        try:
            arc_guard_result = arc.guard(arc, tokens)
        except Exception as e:
            raise ArcGuardRaisesException(arc, tokens) from e
        if not arc_guard_result:
            raise ArcGuardReturnsFalse()

    def _check_transition_guard(self):
        """Checks that the transition guard passes."""
        try:
            guard_result = self.transition.guard(self.transition_inputs())
        except Exception as e:
            raise TransitionGuardRaisesException() from e
        if not guard_result:
            raise TransitionGuardReturnsFalse()

    def input_arcs(self) -> Sequence[CompletedArcPT]:
        return self.net.node_inputs.get(self.transition, ())

    def transition_inputs(self):
        inputs = set()
        for arc in self.input_arcs():
            place = arc.src
            new_place_tokens = set(self.marking.get(place) or set())
            colors_left = dict(arc.weight)
            for token in new_place_tokens.copy():
                if colors_left.get(token.color, 0):
                    inputs.add(token)
                    new_place_tokens.remove(token)
                    colors_left[token.color] -= 1
        return pset(inputs)

    def effects(self) -> PList[Effect]:
        self.check_enabled()
        effects = []
        # Consume inputs.
        inputs = set()
        for arc in self.input_arcs():
            place = arc.src
            colors_left = dict(arc.weight)
            inputs_to_add = set()
            tokens = self.marking.get(place, ())
            for token in tokens:
                if colors_left.get(token.color, 0):
                    inputs_to_add.add(token)
                    effects.append(Consume(arc=arc, token=token))
                    colors_left[token.color] -= 1
            if callable(arc.transform):
                inputs_to_add = arc.transform(inputs_to_add)
            effects.extend(Input(arc=arc, token=token) for token in inputs_to_add)
            inputs.update(inputs_to_add)
        # Calculate outputs.
        output_tokensets = pset(pset(tokenset) for tokenset in self.transition.fn(pset(inputs)))
        # Ensure each output's colorset is unique amongst all outputs.
        # This is to avoid ambiguity when placing tokens into destinations.
        output_tokensets_by_colorset: Mapping[ColorSet, TokenSet] = {
            pmap(Counter(token.color for token in tokenset)): tokenset for tokenset in output_tokensets
        }
        if len(output_tokensets_by_colorset) < len(output_tokensets):
            raise PetriNetTransitionFunctionOutputHasOverlappingColorsets()
        # Produce outputs.
        for arc in self.output_arcs():
            outputs_for_place = output_tokensets_by_colorset[arc.weight]
            effects.extend(Output(arc=arc, token=token) for token in outputs_for_place)
            if callable(arc.transform):
                outputs_for_place = arc.transform(outputs_for_place)
            effects.extend(Produce(arc=arc, token=token) for token in outputs_for_place)
        return plist(effects)

    def output_arcs(self) -> Sequence[CompletedArcTP]:
        return self.net.node_outputs.get(self.transition, ())
