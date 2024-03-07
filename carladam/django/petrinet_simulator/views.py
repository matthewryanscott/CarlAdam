from __future__ import annotations

# Python imports
import json
from typing import Mapping

# Pip imports
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from pyrsistent import pmap

# Internal imports
from carladam import PetriNet
from carladam.django.petrinet_simulator.marking import decode_marking_from_json


def index(request, petrinets: Mapping[str, PetriNet] | None = None):
    if petrinets is None:
        petrinets = getattr(settings, "CARLADAM_SIMULATOR_PETRINETS", {})
    context = {"petrinets": petrinets}
    return render(request, "petrinet_simulator/index.html", context)


def simulator(request, net_name: str, petrinets: Mapping[str, PetriNet] | None = None):
    if petrinets is None:
        petrinets = getattr(settings, "CARLADAM_SIMULATOR_PETRINETS", {})

    net = petrinets.get(net_name)
    if net is None:
        raise Http404()

    colors = pmap((color.label, color) for color in net.colors)

    # Decode initial marking from JSON.
    initial_marking_str = request.GET.get("initial_marking", "{}")
    initial_marking_json = json.loads(initial_marking_str)
    initial_marking = decode_marking_from_json(net=net, colors=colors, marking_json=initial_marking_json)

    # Decode transition list.
    transition_ids_str = request.GET.get("transitions", "")
    transition_ids = list(transition_ids_str.split(","))
    transitions = []
    transitions_by_id = {t.id: t for t in net.transitions}
    for transition_id in transition_ids:
        if not transition_id:
            continue
        transition = transitions_by_id[transition_id]
        transitions.append(transition)

    # Find current marking after transitions.
    current_marking = initial_marking
    for transition in transitions:
        current_marking = net.marking_after_transition(current_marking, transition)

    enabled_transitions = list(sorted(net.enabled_transitions(current_marking)))
    enabled_subnet = PetriNet.new(*(net.subnet(transition) for transition in enabled_transitions))

    context = dict(
        current_marking=current_marking,
        current_marking_items=list(sorted(current_marking.items())),
        enabled_subnet=enabled_subnet,
        enabled_transitions=enabled_transitions,
        example_markings=getattr(net.Structure, "example_markings", {}),
        initial_marking=initial_marking,
        initial_marking_items=list(sorted(initial_marking.items())),
        net=net,
        net_name=net_name,
        transition_ids=",".join(transition.id for transition in transitions),
        transitions=transitions,
    )
    return render(request, "petrinet_simulator/simulator.html", context)
