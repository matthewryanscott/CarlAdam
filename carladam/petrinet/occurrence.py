from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence, TYPE_CHECKING

import attrs
from pyrsistent import plist, pmap, pset
from pyrsistent.typing import PList

from carladam.petrinet.arc import CompletedArcPT, CompletedArcTP
from carladam.petrinet.color import ColorSet
from carladam.petrinet.effects import Consume, Effect, Input, Output, Produce
from carladam.petrinet.errors import PetriNetTransitionFunctionOutputHasOverlappingColorsets
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
        except NotEnabled:
            return False
        return True

    def check_enabled(self):
        if not self.net.node_inputs.get(self.transition) and not self.net.node_outputs.get(self.transition):
            raise NoArcs()
        # Are there enough tokens?
        for arc in self.input_arcs():
            input_colorset = self.input_colorset_for_arc(arc)
            if frozenset(arc.weight.keys()) - frozenset(input_colorset.keys()):
                # Arc weight specifies more colors than Place has.
                raise ArcWeightColorsNotSatisfied()
            if not self.input_colorset_satisfies_weight(arc.weight, input_colorset):
                # Arc weight specifies more of some color token than place contains.
                raise ArcWeightQuantityNotSatisfied()
        # Is the guard satisfied?
        try:
            guard_result = self.transition.guard(self.transition_inputs())
        except Exception as e:
            raise TransitionGuardRaisesException() from e
        if not guard_result:
            raise TransitionGuardReturnsFalse()

    def input_colorset_satisfies_weight(self, weight, colors):
        return all(color in weight and weight[color] <= count for color, count in colors.items())

    def input_colorset_for_arc(self, arc) -> ColorSet:
        return Counter(token.color for token in self.marking.get(arc.src, set()))

    def input_arcs(self) -> Sequence[CompletedArcPT]:
        return self.net.node_inputs.get(self.transition, ())

    def transition_inputs(self):
        inputs = set()
        for arc in self.input_arcs():
            place = arc.src
            new_place_tokens = set(self.marking[place])
            colors_left = dict(arc.weight)
            for token in self.marking[place]:
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
            for token in self.marking[place]:
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


class NotEnabled(Exception):
    pass


class NoArcs(NotEnabled):
    pass


class ArcWeightColorsNotSatisfied(NotEnabled):
    pass


class ArcWeightQuantityNotSatisfied(NotEnabled):
    pass


class TransitionGuardReturnsFalse(NotEnabled):
    pass


class TransitionGuardRaisesException(Exception):
    pass
