"""Provides commonly used classes and functions when using Jupyter notebooks."""

from __future__ import annotations

# Python imports
from functools import lru_cache

# Pip imports
import httpx
from IPython.display import HTML
from jinja2 import Template

# Internal imports
from carladam import (
    Abstract,
    Annotate,
    Color,
    Marking,
    PetriNet,
    Place,
    Token,
    TransformEach,
    Transition,
    __,
    autoname,
    passthrough,
)
from carladam.diagram.digraph import graphviz_digraph
from carladam.diagram.kroki import kroki_image_url, niolesk_edit_url
from carladam.petrinet.defaults import EMPTY_SET


__all__ = [
    "Abstract",
    "Annotate",
    "Color",
    "Marking",
    "PetriNet",
    "Place",
    "Token",
    "TransformEach",
    "Transition",
    "__",
    "autoname",
    "passthrough",
    "report",
]

# Internal imports
from carladam.petrinet.marking import pmarking


@lru_cache
def get_image_svg_text(image_url: str) -> str:
    return httpx.get(image_url).text


def report(net: PetriNet, marking: Marking | None = None, inline: bool = True) -> HTML:
    """Returns a report showing useful information about a `PetriNet` given a `Marking`."""
    marking = pmarking(marking or net.empty_marking())
    # Render diagrams.
    graph_source = graphviz_digraph(net, pmarking(marking), legend=True, legend_width=50)
    graph_image_url = kroki_image_url(diagram_source=graph_source, diagram_type="graphviz")
    graph_image_svg_content = get_image_svg_text(graph_image_url)
    graph_edit_url = niolesk_edit_url(graph_image_url)
    enabled_transitions = set(net.enabled_transitions(marking))
    subnets = {transition: net.subnet(transition) for transition in enabled_transitions}
    subgraph_sources = {
        transition: graphviz_digraph(subnet, marking, legend=True) for transition, subnet in subnets.items()
    }
    subgraph_image_urls = {
        transition: kroki_image_url(diagram_source=subgraph_source, diagram_type="graphviz")
        for transition, subgraph_source in subgraph_sources.items()
    }
    subgraph_image_svg_content = {
        transition: get_image_svg_text(subgraph_image_url)
        for transition, subgraph_image_url in subgraph_image_urls.items()
    }
    subgraph_edit_urls = {
        transition: niolesk_edit_url(subgraph_image_url)
        for transition, subgraph_image_url in subgraph_image_urls.items()
    }
    html = REPORT_TEMPLATE.render(
        EMPTY_SET=EMPTY_SET,
        enabled_transitions=enabled_transitions,
        graph_edit_url=graph_edit_url,
        graph_image_svg_content=graph_image_svg_content,
        graph_image_url=graph_image_url,
        inline=inline,
        subgraph_edit_urls=subgraph_edit_urls,
        subgraph_image_svg_content=subgraph_image_svg_content,
        subgraph_image_urls=subgraph_image_urls,
    )
    return HTML(html)


REPORT_TEMPLATE = Template(
    # language=jinja2
    """
        <div style="display: grid">
            <div style="grid-row: 1 / 2; grid-column: 1 / 3">
                <p><em>Entire net:</em></p>
                <a href="{{ graph_edit_url }}">
                    {% if inline %}
                        {{ graph_image_svg_content | safe }}
                    {% else %}
                        <img src="{{ graph_image_url }}" alt="Petri net graph" />
                    {% endif %}
                </a>
            </div>
            <div style="grid-row: 1 / 2; grid-column: 3 / 4">
                <p><em>Enabled transitions:</em>{% if not enabled_transitions %}{{ EMPTY_SET }}{% endif %}</p>
                {% if enabled_transitions %}
                    {% for transition in enabled_transitions %}
                        <div style="display: inline-block">
                            <a href="{{ subgraph_edit_urls[transition] }}">
                                {% if inline %}
                                    {{ subgraph_image_svg_content[transition] | safe }}
                                {% else %}
                                    <img src="{{ subgraph_image_urls[transition] }}" alt="Petri net subgraph" />
                                {% endif %}
                            </a>
                        </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>
    """
)
