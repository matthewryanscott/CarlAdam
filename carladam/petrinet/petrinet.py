from __future__ import annotations

# Python imports
from collections.abc import Generator, Iterable
from functools import lru_cache
from itertools import chain
from typing import AbstractSet, Iterator, Mapping, Type, cast

# Pip imports
from attr import Factory, define, field
from pyrsistent import PList, PMap, PSet, pmap, pset

# Internal imports
from carladam.petrinet import errors
from carladam.petrinet.color import Abstract, Color
from carladam.petrinet.effects import apply_effects_to_marking
from carladam.petrinet.marking import Marking, PMarking, pmarking
from carladam.petrinet.occurrence import Occurrence
from carladam.petrinet.place import Place
from carladam.petrinet.transition import Transition
from carladam.petrinet.types import (
    Arc,
    ArcTypes,
    CompletedArc,
    CompletedArcTypes,
    PetriNetMember,
    PetriNetMemberOrSet,
    PetriNetNode,
)
from carladam.util.autoname import autoname


class PetriNetMeta(type):
    """Autoname members of the net structure class."""

    def __new__(mcs, name, bases, dct):
        cls = cast(Type["PetriNet"], super().__new__(mcs, name, bases, dct))
        autoname(cls.Structure)
        return cls


@define
class PetriNet(metaclass=PetriNetMeta):
    """A representation of a Petri net."""

    places: PSet[Place] = Factory(pset)
    "The set of ⬭ places contained within this net."

    transitions: PSet[Transition] = Factory(pset)
    "The set of □ transitions contained within this net."

    arcs: PSet[CompletedArc] = Factory(pset)
    "The set of all ⬭→□ and □→⬭ arcs contained within this net."

    node_inputs: PMap[PetriNetNode, PSet[CompletedArc]] = field(factory=pmap, repr=False)
    "Mapping used to find the inputs of a given node."

    node_outputs: PMap[PetriNetNode, PSet[CompletedArc]] = field(factory=pmap, repr=False)
    "Mapping used to find the outputs of a given node."

    structure: object = field(default=Factory(lambda self: self.Structure(), takes_self=True), eq=False, repr=False)
    """Instance of the net structure class for this net."""

    class Structure:
        """Net structure class intended to contain the definition of the Petri net."""

        clusters: Mapping[str, AbstractSet[Place | Transition]] = {}
        """Named clusters to use for visually isolating subgraphs."""

        example_markings: Mapping[str, Marking] = {}
        """Named example markings to show in a Petri net simulator."""

    @classmethod
    def new(cls, *others: PetriNetMemberOrSet):
        """Return a new instance of this class containing its net structure class and any additional members given."""
        net = cls()
        net = net.update_from_structure(net.structure)
        net = net.update(*others)
        return net

    def __contains__(self, obj: PetriNetMemberOrSet | None) -> bool:
        """Returns True if an object (or all of a set of objects) is contained somewhere in the net."""
        if obj is None:
            return False
        if isinstance(obj, Iterable):
            return all(subitem in self for subitem in obj)
        return obj in self.places or obj in self.transitions or obj in self.arcs

    def __hash__(self):
        """Instances are hashable based on their member objects."""
        return hash((self.places, self.transitions, self.node_inputs, self.node_outputs))

    def __iter__(self) -> Iterator[PetriNetMember]:
        """Iterate over all node and arc objects contained in the net."""
        return chain(self.places, self.transitions, self.arcs)

    @property
    def colors(self) -> AbstractSet[Color]:
        """Returns a list of all unique colors specified by the arcs in this net."""
        return self._colors()

    @lru_cache
    def _colors(self):
        if self.arcs:
            return pset(color for arc in self.arcs for color in arc.weight.keys())
        return pset({Abstract})

    def copy(self) -> PetriNet:
        """Returns a new net based on this one."""
        # noinspection PyArgumentList
        return self.__class__(
            places=self.places,
            transitions=self.transitions,
            arcs=self.arcs,
            node_inputs=self.node_inputs,
            node_outputs=self.node_outputs,
            structure=self.structure,
        )

    @lru_cache
    def subnet(self, node: PetriNetNode) -> PetriNet:
        """Return a new net containing only the given node, its input nodes, output nodes, and related arcs."""
        net = PetriNet.new(node)
        for arc in self.node_inputs.get(node, ()):
            net = net.update(arc.src, arc)
        for arc in self.node_outputs.get(node, ()):
            dest = cast(Arc, arc.dest)  # Arc | None -> Arc -- update() guards against None.
            net = net.update(dest, arc)
        return net

    def update(self, *others: PetriNetMemberOrSet) -> PetriNet:
        """Returns a new net based on incorporating the given object(s) into the current net."""
        new = self.copy()
        for other in others:
            if isinstance(other, (list, set, tuple, PList, PSet, Generator)):
                new = new.update(*other)
            elif isinstance(other, type):
                new = new.update(*other.__dict__.values())
            elif isinstance(other, Place) and other not in new.places:
                new.places = new.places.add(other)
            elif isinstance(other, Transition) and other not in new.transitions:
                new.transitions = new.transitions.add(other)
            elif isinstance(other, ArcTypes) and not other.completed:
                raise errors.PetriNetArcIncomplete(other.dest)
            elif isinstance(other, CompletedArcTypes) and other not in new.arcs:
                new = new.update(other.src, other.dest)
                new.arcs = new.arcs.add(other)
                if other.dest is not None:
                    new_inputs = new.node_inputs.get(other.dest, pset())
                    new_inputs = new_inputs.add(other)
                    new.node_inputs = new.node_inputs.set(other.dest, new_inputs)
                if other.src is not None:
                    new_outputs = new.node_outputs.get(other.src, pset())
                    new_outputs = new_outputs.add(other)
                    new.node_outputs = new.node_outputs.set(other.src, new_outputs)
            elif isinstance(other, PetriNet):
                new = new.update(other.places, other.transitions, other.arcs)
        new._reset_caches()
        return new

    def update_from_structure(self, structure: object) -> PetriNet:
        """Return a new net based on current net incorporating a net structure class."""
        object_items = chain(structure.__class__.__dict__.items(), structure.__dict__.items())
        object_values = (value for key, value in object_items if not key.startswith("_"))
        return self.update(object_values)

    def empty_marking(self) -> PMarking:
        """Returns an empty marking of all places in the net."""
        return pmap((place, pset()) for place in self.places)

    def enabled_transitions(self, marking: Marking) -> Iterator[Transition]:
        """Generates the transitions enabled in this net given a `Marking`."""
        for transition in self.transitions:
            if self.transition_is_enabled(marking, transition):
                yield transition

    def marking_after_transition(self, marking: Marking, transition: Transition) -> PMarking:
        """Returns the `Marking` that results from a `Transition` occuring in this net given an initial `Marking`."""
        return self._marking_after_transition(pmarking(marking), transition)

    @lru_cache
    def _marking_after_transition(self, marking: PMarking, transition: Transition) -> PMarking:
        effects = Occurrence(self, marking, transition).effects()
        return apply_effects_to_marking(marking, effects)

    def transition_is_enabled(self, marking: Marking, transition: Transition) -> bool:
        """Returns True if the given `Transition` is enabled in this net given a `Marking`."""
        return self._transition_is_enabled(pmarking(marking), transition)

    @lru_cache
    def _transition_is_enabled(self, marking: PMarking, transition: Transition) -> bool:
        return Occurrence(self, marking, transition).is_enabled()

    def transition_is_external(self, transition: Transition) -> bool:
        """Returns True if a given `Transition` is external in relation to this net."""
        return not self.node_outputs.get(transition) or not self.node_inputs.get(transition)

    def _reset_caches(self):
        self._colors.cache_clear()
        self._marking_after_transition.cache_clear()
        self._transition_is_enabled.cache_clear()
        self.subnet.cache_clear()
