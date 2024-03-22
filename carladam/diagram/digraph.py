"""Generates directed graph diagrams of Petri nets w/ markings using GraphViz."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from textwrap import dedent, wrap
from typing import Callable, DefaultDict, FrozenSet, Optional, Set, Tuple

from jinja2 import Template
from pyrsistent import pmap

from carladam import Place, Transition
from carladam.petrinet import defaults
from carladam.petrinet.arc import ArcPT, CompletedArcPT
from carladam.petrinet.color import colorset_string
from carladam.petrinet.marking import PMarking
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.token import Token
from carladam.petrinet.types import CompletedArc

PLACE_ATTRIBUTES = "[shape=oval]"
TRANSITION_ATTRIBUTES = "[shape=box]"

PLACE_WITH_TOKEN_ATTRIBUTES = "[style=filled,fillcolor=ivory]"

ENABLED_TRANSITION_ATTRIBUTES = "[style=filled,color=blue,fillcolor=skyblue,fontcolor=navyblue]"
DISABLED_TRANSITION_ATTRIBUTES = "[style=filled,color=navyblue,fillcolor=aliceblue,fontcolor=navyblue]"

DISABLED_ARC_PT_ATTRIBUTES = "[color=gray]"
DISABLED_ARC_TP_ATTRIBUTES = "[color=skyblue]"
ENABLED_ARC_PT_ATTRIBUTES = "[color=black,penwidth=2]"
ENABLED_ARC_TP_ATTRIBUTES = "[color=blue,penwidth=2]"

DEFAULT_LEGEND_WIDTH = 25


def token_held_by_place_repr(token: Token) -> str:
    if token.name == token.id:
        return repr(token.color)
    else:
        return f"{token.color!r} {token.name}"


def wrapped(s: str, width: int = 12) -> str:
    return "\n".join(wrap(s, width=width))


EdgeArcWeight = FrozenSet
EdgeArcAnnotation = Optional[str]
EdgeArcsKey = Tuple[EdgeArcWeight, EdgeArcAnnotation, Place, Transition]
EdgeArcs = DefaultDict[EdgeArcsKey, Set[CompletedArc]]


def always_none(transition):
    return None


@lru_cache
def graphviz_digraph(
    net: PetriNet,
    marking: PMarking = pmap(),
    /,
    legend: bool = False,
    rotate: bool = False,
    legend_width: int = DEFAULT_LEGEND_WIDTH,
    transition_url_fn: Callable[[Transition], str] | None = None,
) -> str:
    """Return a GraphViz representation of a `PetriNet`."""
    transition_url_fn = transition_url_fn or always_none

    marking_repr = {
        place: "".join(token_held_by_place_repr(token) for token in sorted(tokens)) for place, tokens in marking.items()
    }

    arcs = set(net.arcs)
    double_arcs = set()
    edge_arcs: EdgeArcs = defaultdict(set)
    for arc in arcs:
        if isinstance(arc, ArcPT):
            place = arc.src
            transition = arc.dest
        else:
            place = arc.dest
            transition = arc.src
        edge_arcs[(frozenset(arc.weight.items()), arc.annotation, place, transition)].add(arc)
    for pair in edge_arcs.values():
        if len(pair) != 2:
            continue
        for arc in pair:
            arcs.remove(arc)
            if isinstance(arc, CompletedArcPT):
                double_arcs.add(arc)

    sorted_places = list(sorted(net.places))
    enabled_transitions = set(net.enabled_transitions(marking))
    disabled_transitions = net.transitions.difference(enabled_transitions)
    sorted_enabled_transitions = list(sorted(enabled_transitions))
    sorted_disabled_transitions = list(sorted(disabled_transitions))
    graphviz_source = GRAPHVIZ_DIGRAPH_TEMPLATE.render(
        DISABLED_ARC_PT_ATTRIBUTES=DISABLED_ARC_PT_ATTRIBUTES,
        DISABLED_ARC_TP_ATTRIBUTES=DISABLED_ARC_TP_ATTRIBUTES,
        DISABLED_TRANSITION_ATTRIBUTES=DISABLED_TRANSITION_ATTRIBUTES,
        EMPTY_SET=defaults.EMPTY_SET,
        ENABLED_ARC_PT_ATTRIBUTES=ENABLED_ARC_PT_ATTRIBUTES,
        ENABLED_ARC_TP_ATTRIBUTES=ENABLED_ARC_TP_ATTRIBUTES,
        ENABLED_TRANSITION_ATTRIBUTES=ENABLED_TRANSITION_ATTRIBUTES,
        PLACE_ATTRIBUTES=PLACE_ATTRIBUTES,
        PLACE_WITH_TOKEN_ATTRIBUTES=PLACE_WITH_TOKEN_ATTRIBUTES,
        TRANSITION_ATTRIBUTES=TRANSITION_ATTRIBUTES,
        arcs=sorted(arcs),
        clusters=getattr(net.structure, "clusters", {}),
        colorset_string=colorset_string,
        disabled_transitions=sorted_disabled_transitions,
        double_arcs=sorted(double_arcs),
        enabled_transitions=sorted_enabled_transitions,
        enumerate=enumerate,
        legend=legend,
        legend_width=legend_width,
        marking=marking,
        marking_repr=marking_repr,
        places=sorted_places,
        rotate=rotate,
        sorted=sorted,
        str=str,
        transition_url_fn=transition_url_fn,
        wrap=wrap,
        wrapped=wrapped,
    )
    return dedent(graphviz_source)


# noinspection HtmlDeprecatedAttribute
GRAPHVIZ_DIGRAPH_TEMPLATE = Template(
    # language=jinja2
    """
    digraph {
        layout=dot
        overlap=false
        {% if rotate %}rankdir=LR{% endif %}
        {
            node [fontname="-apple-system,BlinkMacSystemFont,sans-serif"]
            edge [fontname="-apple-system,BlinkMacSystemFont,sans-serif"]
            graph [color=lightgray,fontcolor=lightgray,fontname="-apple-system,BlinkMacSystemFont,sans-serif"]

            node {{ PLACE_ATTRIBUTES }}
            {% for place in places %}
                n_{{ place.id }}
                [label="{{ wrapped(place.name) }}{% if marking_repr.get(place) %}\n{{ marking_repr[place] }}{% endif %}"]
                {% if marking[place] -%}
                    {{ PLACE_WITH_TOKEN_ATTRIBUTES }}
                {%- endif %}
            {% endfor %}

            node {{ TRANSITION_ATTRIBUTES }}
            {% for transition in enabled_transitions %}
                n_{{ transition.id }}
                {{ ENABLED_TRANSITION_ATTRIBUTES }}
                [label="{{ wrapped(transition.name) }}{% if transition.annotation %}\n\n{{ transition.annotation }}{% endif %}"]
                {% set transition_url = transition_url_fn(transition) %}
                {% if transition_url %}
                    [URL="{{ transition_url }}"]
                {% endif %}
            {% endfor %}
            {% for transition in disabled_transitions %}
                n_{{ transition.id }}
                {{ DISABLED_TRANSITION_ATTRIBUTES }}
                [label="{{ wrapped(transition.name) }}{% if transition.annotation %}\n\n{{ transition.annotation }}{% endif %}"]
            {% endfor %}

            {% for arc in arcs %}
                n_{{ arc.src.id }}->n_{{ arc.dest.id }}
                [label="{{ colorset_string(arc.weight) }}{% if arc.annotation %} {{ wrapped(arc.annotation) }}{% endif %}"]
                {% if arc.src in places -%}
                    {%- if arc.dest in enabled_transitions -%}
                        {{ ENABLED_ARC_PT_ATTRIBUTES }}
                    {%- else -%}
                        {{ DISABLED_ARC_PT_ATTRIBUTES }}
                    {%- endif -%}
                {%- else -%}
                    {%- if arc.src in enabled_transitions -%}
                        {{ ENABLED_ARC_TP_ATTRIBUTES }}
                    {%- else -%}
                        {{ DISABLED_ARC_TP_ATTRIBUTES }}
                    {%- endif -%}
                {%- endif %}
            {% endfor %}

            {% for arc in double_arcs %}
                n_{{ arc.src.id }}->n_{{ arc.dest.id }}
                [label="{{ colorset_string(arc.weight) }}{% if arc.annotation %} {{ wrapped(arc.annotation) }}{% endif %}"]
                [dir=both]
                {%- if arc.dest in enabled_transitions -%}
                    {{ ENABLED_ARC_PT_ATTRIBUTES }}
                {%- else -%}
                    {{ DISABLED_ARC_PT_ATTRIBUTES }}
                {%- endif -%}
            {% endfor %}

            {% for index, (name, cluster) in enumerate(clusters.items()) %}
                subgraph cluster_{{ index }} {
                    label="{{ name }}"
                    {% for item in cluster %}
                        n_{{ item.id }}
                    {% endfor %}
                }
            {% endfor %}
        }
        {% if marking and legend %}
            {
                rank=max
                MarkingLegend [shape=none, margin=0, label=<
                    <table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                        <tr>
                            <td colspan="2"><b>Marking</b></td>
                        </tr>
                        {% for place, tokens in sorted(marking.items()) %}
                            {% if place in places and tokens %}
                                <tr>
                                    <td align="left" valign="top">{{ place.name }}:</td>
                                    <td align="left" valign="top">{% for token in tokens -%}
                                        {%- for line in wrap(str(token), legend_width) -%}
                                            {{ line }}
                                            {%- if not loop.last %}<br/>  {% endif -%}
                                        {%- endfor -%}
                                        {%- if not loop.last %}<br/>{% endif -%}
                                    {%- endfor %}</td>
                                </tr>
                            {% endif %}
                        {% endfor %}
                    </table>
                >]
            }
        {% endif %}
    }
    """  # noqa: E501 line too long
)
