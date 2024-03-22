from typing import Callable, Dict

import networkx as nx
from numpy.typing import ArrayLike

from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.types import PetriNetNode

NodeCoordinates = Dict[PetriNetNode, ArrayLike]
LayoutFunction = Callable[..., NodeCoordinates]


def auto_layout_nodes(net: PetriNet, algorithm: LayoutFunction = nx.spring_layout, **kwargs) -> NodeCoordinates:
    """Automatically layout node geometry based on a layout function."""
    graph = networkx_graph(net)
    return algorithm(graph, **kwargs)


def networkx_graph(net: PetriNet) -> nx.Graph:
    """Transforms a `PetriNet` into a `Graph` suitable for processing with `networkx`."""
    graph = nx.Graph()
    graph.add_nodes_from(net.places)
    graph.add_nodes_from(net.transitions)
    for arc in net.arcs:
        graph.add_edge(arc.src, arc.dest)
    return graph
