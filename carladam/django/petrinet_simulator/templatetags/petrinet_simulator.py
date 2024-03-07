from __future__ import annotations

# Python imports
import json
from functools import lru_cache
from textwrap import dedent
from typing import Sequence
from urllib.parse import quote

# Pip imports
import httpx
from django import template
from django.utils.safestring import SafeString
from markdown import markdown as _markdown
from pyrsistent import PMap, thaw

# Internal imports
from carladam import Marking, PetriNet, Transition
from carladam.diagram.digraph import graphviz_digraph
from carladam.diagram.kroki import kroki_image_url, niolesk_edit_url
from carladam.diagram.sequence import plantuml_sequence_diagram
from carladam.petrinet.marking import PMarking, pmarking
from carladam.petrinet.types import PetriNetNode


register = template.Library()


@register.filter
def markdown(source: str):
    return SafeString(_markdown(source))


@register.filter
def net_title(net: PetriNet):
    return (net.__doc__ or "").lstrip().split("\n", 1)[0]


@register.filter
def net_description(net: PetriNet):
    _, *rest = (net.__doc__ or "").lstrip().split("\n", 1)
    return dedent(rest[0]).lstrip().rstrip() if rest else ""


@register.simple_tag
def net_graph_image_data(
    net: PetriNet,
    initial_marking: PMarking,
    transition_ids_str: str,
    current_marking: PMarking,
    legend: bool = True,
) -> str:
    def transition_url_fn(t: Transition) -> str:
        return f"?initial_marking={marking_encoded(initial_marking)}&transitions={transition_ids_str},{t.id}"

    diagram_source = graphviz_digraph(net, current_marking, legend=legend, transition_url_fn=transition_url_fn)
    image_url = kroki_image_url(diagram_source=diagram_source, diagram_type="graphviz", image_format="svg")
    image_source = _image_source(image_url)
    return SafeString(image_source)


@register.simple_tag
def net_graph_niolesk_url(
    net: PetriNet,
    initial_marking: PMarking,
    transition_ids_str: str,
    current_marking: PMarking,
    legend: bool = True,
) -> str:
    def transition_url_fn(t: Transition) -> str:
        return f"?initial_marking={marking_encoded(initial_marking)}&transitions={transition_ids_str},{t.id}"

    diagram_source = graphviz_digraph(net, current_marking, legend=legend, transition_url_fn=transition_url_fn)
    image_url = kroki_image_url(diagram_source=diagram_source, diagram_type="graphviz", image_format="svg")
    return niolesk_edit_url(image_url=image_url)


@register.simple_tag
def net_run_sequence_diagram_image_data(
    net: PetriNet,
    initial_marking: PMarking,
    transitions: Sequence[Transition],
) -> str:
    diagram_source = plantuml_sequence_diagram(net=net, initial_marking=initial_marking, transitions=transitions)
    image_url = kroki_image_url(diagram_source=diagram_source, diagram_type="plantuml", image_format="svg")
    image_source = _image_source(image_url)
    return SafeString(image_source)


@register.simple_tag
def net_run_sequence_diagram_niolesk_url(
    net: PetriNet,
    initial_marking: PMarking,
    transitions: Sequence[Transition],
) -> str:
    diagram_source = plantuml_sequence_diagram(net=net, initial_marking=initial_marking, transitions=transitions)
    image_url = kroki_image_url(diagram_source=diagram_source, diagram_type="plantuml", image_format="svg")
    return niolesk_edit_url(image_url=image_url)


@register.filter
def marking_encoded(marking: Marking):
    if not isinstance(marking, PMap):
        marking = pmarking(marking)
    return _marking_encoded(marking)


@lru_cache
def _marking_encoded(marking: PMarking):
    marking_json = {
        place.id: [
            {
                "id": token.id,
                "color": token.color.label,
                "data": token.data,
            }
            for token in tokens
        ]
        for place, tokens in marking.items()
    }
    return quote(json.dumps(thaw(marking_json)))


@register.filter
def net_subnet(net: PetriNet, node: PetriNetNode):
    return net.subnet(node)


@lru_cache
def _image_source(image_url: str) -> str:
    return httpx.get(image_url).text
