import pytest
from pyrsistent import pset

from carladam.petrinet import errors
from carladam.petrinet.arc import (
    Annotate,
    CompletedArcPT,
    CompletedArcTP,
    TransformEach,
    arc,
    arc_path,
    inhibitor_arc,
    weights_are_satisfied,
)
from carladam.petrinet.color import Abstract, Color
from carladam.petrinet.marking import marking_colorset
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token
from carladam.petrinet.transition import Transition, passthrough


@pytest.mark.parametrize("ltr", [True, False])
def test_from_place_to_transition(ltr: bool):
    net = PetriNet.new(
        p0 := Place(),
        t0 := Transition(),
        a0 := p0 >> t0 if ltr else t0 << p0,
    )
    assert a0.src == p0
    assert a0.dest == t0
    assert not net.node_inputs.get(p0)
    assert net.node_outputs[p0] == {a0}
    assert net.node_inputs[t0] == {a0}
    assert not net.node_outputs.get(t0)


@pytest.mark.parametrize("ltr", [True, False])
def test_from_transition_to_place(ltr: bool):
    net = PetriNet.new(
        p0 := Place(),
        t0 := Transition(),
        a0 := t0 >> p0 if ltr else p0 << t0,
    )
    assert a0.src == t0
    assert a0.dest == p0
    assert not net.node_inputs.get(t0)
    assert net.node_outputs[t0] == {a0}
    assert net.node_inputs[p0] == {a0}
    assert not net.node_outputs.get(p0)


def test_from_place_to_place_not_valid():
    with pytest.raises(TypeError):
        Place() >> Place()  # type: ignore
    with pytest.raises(TypeError):
        Place() << Place()  # type: ignore


def test_from_transition_to_transition_not_valid():
    with pytest.raises(TypeError):
        Transition() >> Transition()  # type: ignore
    with pytest.raises(TypeError):
        Transition() << Transition()  # type: ignore


def test_is_hashable():
    p0, t0, p1 = Place(), Transition(), Place()
    a0 = p0 >> t0
    a1 = t0 >> p1
    a2 = t0 >> p1
    s = {a0, a1}
    s.update({a2})
    assert len(s) == 2


def test_weight():
    net = PetriNet.new(
        p0a := Place(),
        p0b := Place(),
        t0 := Transition(fn=Abstract.produce(3)),
        p1 := Place(),
        p0a >> t0,
        p0b >> {Abstract: 2} >> t0,
        t0 >> {Abstract: 3} >> p1,
    )

    m0 = {
        p0a: {Token()},
        p0b: {Token()},
    }
    assert not net.transition_is_enabled(m0, t0)
    m0 = {
        p0a: {Token()},
        p0b: {Token(), Token()},
    }
    assert net.transition_is_enabled(m0, t0)
    m1 = net.marking_after_transition(m0, t0)
    assert marking_colorset(m1) == {
        p1: {Abstract: 3},
    }


def test_weight_shorthand_using_color():
    p = Place()
    t = Transition()
    c = Color("C")

    assert (p >> c >> t).weight == {c: 1}
    assert (p << c << t).weight == {c: 1}
    assert (t >> c >> p).weight == {c: 1}
    assert (t << c << p).weight == {c: 1}


def test_weight_shorthand_using_sets():
    p = Place()
    t = Transition()
    c0 = Color("0")
    c1 = Color("1")
    expected_weight = {c0: 1, c1: 1}
    a0 = p >> {c0, c1} >> t
    a1 = p >> frozenset({c0, c1}) >> t
    a2 = p >> pset({c0, c1}) >> t
    a3 = t >> {c0, c1} >> p
    a4 = t >> frozenset({c0, c1}) >> p
    a5 = t >> pset({c0, c1}) >> p
    assert all(expected_weight == a.weight for a in [a0, a1, a2, a3, a4, a5])


def test_annotate():
    p = Place()
    t = Transition()
    a0 = p >> t >> Annotate("A0")
    a1 = t >> Abstract >> Annotate("A1") >> p
    assert a0.annotation == "A0"
    assert "A0" in repr(a0)
    assert a1.annotation == "A1"


def test_incomplete():
    net = PetriNet.new(p := Place())
    a = p >> Abstract >> Annotate("A")
    with pytest.raises(errors.PetriNetArcIncomplete):
        net.update(a)


def test_transform_each():
    def x_plus_1(token):
        return token.replace(x=token.data.get("x", 0) + 1)

    def x_minus_2(token):
        return token.replace(x=token.data.get("x", 0) - 2)

    net = PetriNet.new(
        p := Place(),
        t := Transition(fn=passthrough()),
        a0 := (p >> t >> TransformEach(x_plus_1)),  # [TODO] p >> TransformEach(x_plus_1) >> t
        t >> p >> TransformEach(x_minus_2),
    )
    assert a0.transform is not None

    m0 = {p: {Token()}}
    m1 = net.marking_after_transition(m0, t)
    assert marking_colorset(m1) == {p: {Abstract: 1}}
    token = next(iter(m1[p]))
    assert token.data["x"] == -1


def test_sorts_by_src_name_then_dest_name():
    p = Place("P")
    t = Transition("T")
    a0 = t >> p
    a1 = p >> t
    assert list(sorted([a0, a1])) == [a1, a0]


def test_lshift_equivalence():
    p = Place()
    t = Transition()
    c0 = Color("0")
    c1 = Color("1")

    assert p >> {c0, c1} >> t == t << {c0, c1} << p
    assert p >> frozenset({c0, c1}) >> t == t << frozenset({c0, c1}) << p
    assert p >> pset({c0, c1}) >> t == t << pset({c0, c1}) << p

    assert t >> {c0, c1} >> p == p << {c0, c1} << t
    assert t >> frozenset({c0, c1}) >> p == p << frozenset({c0, c1}) << t
    assert t >> pset({c0, c1}) >> p == p << pset({c0, c1}) << t

    assert p >> t >> Annotate("A0") == t << p << Annotate("A0")
    assert t >> Abstract >> Annotate("A1") >> p == p << Abstract << Annotate("A1") << t


def test_cannot_overwrite_already_set_endpoints():
    p = Place()
    t = Transition()

    arc = p << {Abstract: 1}
    with pytest.raises(errors.PetriNetArcIncomplete):
        arc >> p

    arc = t << {Abstract: 1}
    with pytest.raises(errors.PetriNetArcIncomplete):
        arc >> t

    arc = p >> {Abstract: 1}
    with pytest.raises(errors.PetriNetArcIncomplete):
        arc << p

    arc = t >> {Abstract: 1}
    with pytest.raises(errors.PetriNetArcIncomplete):
        arc << t


def test_arc_pt_guard():
    def inhibitor(arc, tokens):
        return not tokens

    net = PetriNet.new(
        p_input := Place(),
        p_yes := Place(),
        p_no := Place(),
        t_yes := Transition(),
        t_no := Transition(),
        p_input >> t_yes,  # default guard is to require an abstract token to be present
        (p_input >> t_no)(guard=inhibitor),
        t_yes >> p_yes,
        t_no >> p_no,
    )

    yes_is_enabled = {p_input: {Token()}}
    no_is_enabled = {}

    assert net.transition_is_enabled(yes_is_enabled, t_yes)
    assert not net.transition_is_enabled(yes_is_enabled, t_no)

    assert not net.transition_is_enabled(no_is_enabled, t_yes)
    assert net.transition_is_enabled(no_is_enabled, t_no)


def test_arc_pt_guard_raises_exception():
    def guard_raises_exception(arc, tokens):
        raise ValueError("This guard always raises an exception")

    net = PetriNet.new(
        p := Place(),
        t := Transition(),
        (p >> t)(guard=guard_raises_exception),
    )

    with pytest.raises(errors.ArcGuardRaisesException) as e:
        net.transition_is_enabled({p: {Token()}}, t)
    assert isinstance(e.value.__cause__, ValueError)


def test_arc_factory_place_transition():
    p = Place()
    t = Transition()
    a = arc(p, t)
    assert isinstance(a, CompletedArcPT)
    assert a.src == p
    assert a.dest == t
    assert a.weight == {Abstract: 1}
    assert a.annotation is None
    assert a.transform is None
    assert a.guard is weights_are_satisfied


def test_arc_factory_place_transition_colorset():
    p = Place()
    t = Transition()
    c = Color("c")
    a = arc(p, t, {c: 2})
    assert isinstance(a, CompletedArcPT)
    assert a.src == p
    assert a.dest == t
    assert a.weight == {c: 2}
    assert a.annotation is None
    assert a.transform is None
    assert a.guard is weights_are_satisfied


@pytest.mark.parametrize(
    "weight, actual_weight",
    [
        (None, {Abstract: 1}),
        (Abstract, {Abstract: 1}),
        ({Abstract: 2}, {Abstract: 2}),
    ],
)
def test_arc_factory_transition_place_colorset(weight, actual_weight):
    p = Place()
    t = Transition()
    a = arc(t, p, weight)
    assert isinstance(a, CompletedArcTP)
    assert a.src == t
    assert a.dest == p
    assert a.weight == actual_weight
    assert a.annotation is None
    assert a.transform is None


def test_arc_factory_transition_place():
    p = Place()
    t = Transition()
    a = arc(t, p)
    assert isinstance(a, CompletedArcTP)
    assert a.src == t
    assert a.dest == p
    assert a.weight == {Abstract: 1}
    assert a.annotation is None
    assert a.transform is None


@pytest.mark.parametrize(
    "src, dest",
    [
        (Place(), Place()),
        (Transition(), Transition()),
    ],
)
def test_arc_factory_raises_type_error_for_incompatible_nodes(src, dest):
    with pytest.raises(TypeError):
        arc(src, dest)


def test_arc_path():
    p1, p2, p3 = Place(), Place(), Place()
    t1, t2 = Transition(), Transition()
    assert list(arc_path(p1, t1, p2, t2, p3)) == [arc(p1, t1), arc(t1, p2), arc(p2, t2), arc(t2, p3)]


def test_inhibitor_arc():
    net = PetriNet.new(
        p0 := Place(),
        t := Transition(),
        p1 := Place(),
        inhibitor_arc(p0, t),
        arc(t, p1),
    )
    assert marking_colorset(net.marking_after_transition({}, t)) == {p1: {Abstract: 1}}
    assert not net.transition_is_enabled({p0: {Abstract()}}, t)
