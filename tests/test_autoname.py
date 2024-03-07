# Internal imports
from carladam import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.transition import Transition
from carladam.util.autoname import autoname


def test_autoname():
    autoname(p2 := Place())
    assert p2.name == "P2"


def test_autoname_ignores_underscore():
    autoname(_ := Place())
    assert _.name != "_"


def test_autoname_ignores_other_object_types():
    class SomethingWithName:
        def __init__(self):
            self.name = "id"
            self.id = "id"

    autoname(obj := SomethingWithName())
    assert obj.name == "id"


def test_autoname_ignores_already_named():
    autoname(p0 := Place(name="P0"))
    assert p0.name == "P0"


def test_autoname_ignores_objects_not_being_named():
    p0 = Place()
    autoname(p1 := Place())
    assert p0.name == p0.id
    assert p1.name == "P1"


def test_autoname_petrinet_structure_subclass():
    class ExampleNet(PetriNet):
        class Structure:
            class P:
                p0 = Place()

            class T:
                t0 = Transition()

            arcs = {
                P.p0 >> T.t0,
                T.t0 >> P.p0,
            }

    assert ExampleNet.Structure.P.p0.name == "P0"
    assert ExampleNet.Structure.T.t0.name == "T0"
