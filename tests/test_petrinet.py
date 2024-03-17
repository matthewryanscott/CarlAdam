# Pip imports
import pytest

# Internal imports
from carladam import Abstract, Color, Token
from carladam.petrinet import errors
from carladam.petrinet.occurrence import NotEnabled
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.transition import Transition, always


def test_can_be_created():
    PetriNet()


def test_contain_places():
    net = PetriNet()

    p0 = Place()
    assert p0 not in net
    net = net.update(p0)
    assert p0 in net

    p1, p2 = Place(), Place()
    assert {p1, p2} not in net
    net = net.update(p1, p2)
    assert {p1, p2} in net


def test_contain_transitions():
    net = PetriNet()

    t0 = Transition()
    assert t0 not in net
    net = net.update(t0)
    assert t0 in net

    t1, t2 = Transition(), Transition()
    assert {t1, t2} not in net
    net = net.update(t1, t2)
    assert {t1, t2} in net


def test_contain_arcs():
    net = PetriNet.new(
        p0 := Place(),
        t0 := Transition(),
        p1 := Place(),
    )
    a0 = p0 >> t0
    a1 = t0 >> p1
    assert a0 not in net
    assert a1 not in net

    net = net.update(a0, a1)
    assert a0 in net
    assert a1 in net

    t1 = Transition()
    a2 = p1 >> t1
    net = net.update(a2)

    px, tx = Place(), Transition()
    ax = px >> tx
    assert px not in net
    assert px not in net
    net2 = net.update(ax)
    assert px in net2
    assert tx in net2

    # Arcs are not automatically added when related objects are added.
    net3 = net.update(px, tx)
    assert ax not in net3


def test_not_contain_none():
    net = PetriNet.new(None)
    assert None not in net


def test_guard_can_prevent_transition():
    net = PetriNet.new(
        p0 := Place(),
        t0 := Transition(guard=always(False)),
        p1 := Place(),
        p0 >> t0,
        t0 >> p1,
    )
    marking = {p0: {Token()}}
    assert not net.transition_is_enabled(marking, t0)


def test_transition_is_not_enabled_if_disconnected():
    net = PetriNet.new(t := Transition())
    assert not net.transition_is_enabled({}, t)
    with pytest.raises(NotEnabled):
        net.marking_after_transition({}, t)


def test_transition_must_output_unique_colorsets():
    def generates_two_identical_colorsets(inputs):
        yield {Abstract()}
        yield {Abstract()}

    net = PetriNet.new(
        p0 := Place(),
        t0 := Transition(fn=generates_two_identical_colorsets),
        p1 := Place(),
        p0 >> t0,
        t0 >> p1,
    )
    with pytest.raises(errors.PetriNetTransitionFunctionOutputHasOverlappingColorsets):
        net.marking_after_transition({p0: {Abstract()}}, t0)


def test_subnet():
    net = PetriNet.new(
        p0 := Place(),
        p1 := Place(),
        p2 := Place(),
        p3 := Place(),
        t0 := Transition(),
        t1 := Transition(),
        a0 := p0 >> t0,
        a1 := t0 >> p1,
        a2 := p1 >> t1,
        a3 := t1 >> p2,
        a4 := t1 >> p3,
    )
    assert set(net.subnet(p0)) == {p0, a0, t0}
    assert set(net.subnet(p1)) == {p1, t0, t1, a1, a2}
    assert set(net.subnet(p2)) == {p2, t1, a3}
    assert set(net.subnet(p3)) == {p3, t1, a4}
    assert set(net.subnet(t0)) == {t0, p0, p1, a0, a1}
    assert set(net.subnet(t1)) == {t1, p1, p2, p3, a2, a3, a4}


def test_eq():
    net0 = PetriNet.new(
        p0 := Place(),
        t0 := Transition(),
        p1 := Place(),
        p0 >> t0,
        t0 >> p1,
    )
    net1 = net0.update(
        p2 := Place(),
        t0 >> p2,
    )
    assert net0.copy() == net0
    assert net0 != net1


def test_subclass_with_structure():
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

    net = ExampleNet.new()

    p0 = net.structure.P.p0
    t0 = net.structure.T.t0

    assert p0 in net
    assert t0 in net
    assert (p0 >> t0) in net
    assert (t0 >> p0) in net


def test_colors():
    c0 = Color("0")
    c1 = Color("1")

    class NetWithColors(PetriNet):
        class Structure:
            p = Place()
            t = Transition()
            arcs = {
                p >> c0 >> t,
                t >> c1 >> p,
            }

    net = NetWithColors.new()
    assert net.colors == {c0, c1}

    class EmptyNet(PetriNet):
        class Structure:
            arcs = set()

    net = EmptyNet.new()
    assert net.colors == {Abstract}


def test_composition():
    p0, p1 = Place(), Place()
    t0 = Transition()
    net0 = PetriNet.new(p0 >> t0)
    net1 = PetriNet.new(t0 >> p1)
    composed = PetriNet.new(net0, net1)
    assert p0 in composed
    assert p1 in composed
    assert t0 in composed
    assert p0 >> t0 in composed
    assert t0 >> p1 in composed
