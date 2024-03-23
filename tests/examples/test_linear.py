from pyrsistent import s

from carladam import arc
from carladam.petrinet.color import Abstract
from carladam.petrinet.marking import marking_colorset
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token
from carladam.petrinet.transition import Transition


class LinearNet(PetriNet):
    class Structure:
        p0 = Place()
        p1 = Place()

        t0 = Transition()

        arcs = {
            arc(p0, t0),
            arc(t0, p1),
        }


def test_fire_transitions():
    net = LinearNet.new()
    ns = LinearNet.Structure
    m0 = net.empty_marking().update({ns.p0: s(*Token() * 5)})
    assert marking_colorset(m0) == {
        ns.p0: {Abstract: 5},
    }

    m1 = net.marking_after_transition(m0, ns.t0)
    m1_colorset = marking_colorset(m1)
    expected_m1_colorset = {
        ns.p0: {Abstract: 4},
        ns.p1: {Abstract: 1},
    }
    assert m1_colorset == expected_m1_colorset
