# Python imports
from functools import lru_cache
from typing import Mapping

# Pip imports
from pyrsistent import freeze
from pyrsistent.typing import PMap

# Internal imports
from carladam import Color, PetriNet, Token
from carladam.petrinet.marking import MutableMarking, PMarking, pmarking


def decode_marking_from_json(net: PetriNet, colors: Mapping[str, Color], marking_json: Mapping) -> PMarking:
    if not isinstance(marking_json, PMap):
        marking_json = freeze(marking_json)
    if not isinstance(colors, PMap):
        colors = freeze(colors)
    return _decode_marking_from_json(net, colors, marking_json)


@lru_cache
def _decode_marking_from_json(net: PetriNet, colors: Mapping[str, Color], marking_json: PMap) -> PMarking:
    _initial_marking: MutableMarking = {}
    for place in net.places:
        if place.id not in marking_json:
            continue
        place_marking = _initial_marking[place] = set()
        for token_json in marking_json[place.id]:
            token = Token(
                id=token_json["id"],
                color=colors[token_json["color"]],
                data=token_json["data"],
            )
            place_marking.add(token)
    return pmarking(_initial_marking)
