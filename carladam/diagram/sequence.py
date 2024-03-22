"""Generates sequence diagrams of Petri net runs using PlantUML."""

from __future__ import annotations

from functools import lru_cache
from textwrap import wrap
from typing import Sequence

from pyrsistent import plist, pmap
from pyrsistent.typing import PList as PListType

from carladam import PetriNet, Place, Token, Transition
from carladam.petrinet.marking import PMarking, pmarking


def token_held_by_place_repr(token: Token) -> str:
    if token.name == token.id:
        return repr(token.color)
    else:
        return f"{token.color!r} {token.name}"


def wrapped(s: str, width: int = 12) -> str:
    return "\\n".join(wrap(s, width=width))


def plantuml_sequence_diagram(
    net: PetriNet,
    initial_marking: PMarking = pmap(),
    transitions: Sequence[Transition] = plist(),
) -> str:
    """Return a PlantUML representation of a run given a net, initial marking, and sequence of transitions."""
    return _plantuml_sequence_diagram(
        net=net,
        initial_marking=pmarking(initial_marking),
        transitions=plist(transitions),
    )


@lru_cache
def _plantuml_sequence_diagram(
    net: PetriNet,
    initial_marking: PMarking = pmap(),
    transitions: PListType[Transition] = plist(),
) -> str:
    places_added: set[Place] = set()
    transitions_added: set[Transition] = set()

    participants: list[str] = []
    events: list[str] = []

    header = ["!pragma teoz true"]

    def add_place(p: Place):
        if p in places_added:
            return
        print("add_place", p)
        places_added.add(p)
        participants.append(f'queue "{wrapped(p.name)}" as p_{p.id}')

    def add_transition(t: Transition):
        if t in transitions_added:
            return
        print("add_transition", t)
        transitions_added.add(t)
        participants.append(f'participant "{wrapped(t.name)}" as t_{t.id}')

    def add_marking_event(marking: PMarking):
        print("add_marking_event")
        for place, tokens in marking.items():
            if tokens:
                add_place(place)
        marking_repr = {
            place: "".join(token_held_by_place_repr(token) for token in sorted(tokens))
            for place, tokens in marking.items()
        }
        marking_notes = "\n& ".join(
            f"note over p_{place.id}\n{marking_repr[place]}\nend note" for place, tokens in marking.items() if tokens
        )
        events.append(marking_notes)

    def add_transition_event(transition: Transition):
        print("add_transition_event", transition)
        add_transition(transition)
        transition_arcs = "".join(
            [
                "\n& ".join(f"p_{arc.src.id} x-> t_{transition.id}" for arc in net.node_inputs.get(transition, ())),
                f"\nactivate t_{transition.id} #skyblue\n",
                "\n& ".join(f"t_{transition.id} ->o p_{arc.dest.id}" for arc in net.node_outputs.get(transition, ())),
                f"\ndeactivate t_{transition.id}\n",
            ]
        )
        events.append(transition_arcs)

    current_marking = initial_marking
    add_marking_event(current_marking)
    for current_transition in transitions:
        add_transition_event(current_transition)
        current_marking = net.marking_after_transition(current_marking, current_transition)
        add_marking_event(current_marking)

    return "\n".join(header + participants + participants + events)
