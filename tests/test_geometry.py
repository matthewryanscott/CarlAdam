# Internal imports
from carladam.diagram.geometry import auto_layout_nodes
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.transition import Transition


def test_auto_layout():
    net = PetriNet.new(
        p0 := Place(),
        t0 := Transition(),
        p1 := Place(),
        p0 >> t0,
        t0 >> p1,
    )
    coordinates = auto_layout_nodes(net)
    assert tuple(coordinates[p0]) != tuple(coordinates[t0])
    assert tuple(coordinates[p0]) != tuple(coordinates[p1])
