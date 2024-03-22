import pytest
from pyrsistent import s

from carladam.petrinet.color import Abstract
from carladam.petrinet.marking import marking_colorset
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token
from carladam.petrinet.transition import Transition


class LinearNet(PetriNet):
    class Structure:
        class P:
            p0 = Place()
            p1 = Place()

        class T:
            t0 = Transition()

        arcs = {
            P.p0 >> T.t0,
            T.t0 >> P.p1,
        }


@pytest.fixture
def net():
    return LinearNet.new()


@pytest.fixture
def structure(net) -> LinearNet.Structure:
    return net.structure


def test_fire_transitions(net, structure):
    P = structure.P
    T = structure.T
    m0 = net.empty_marking().update({P.p0: s(Token(), Token())})
    assert marking_colorset(m0) == {
        P.p0: {Abstract: 2},
    }

    m1 = net.marking_after_transition(m0, T.t0)
    m1_colorset = marking_colorset(m1)
    expected_m1_colorset = {
        P.p0: {Abstract: 1},
        P.p1: {Abstract: 1},
    }
    assert m1_colorset == expected_m1_colorset
