from pyrsistent import s

from carladam import Color
from carladam.petrinet.transition import Transition, passthrough


def test_can_be_created():
    Transition()


def test_is_hashable():
    t0, t1 = Transition(), Transition()
    s = {t0, t1}
    s.update({t1})
    assert len(s) == 2


def test_has_auto_assigned_id():
    assert Transition().id is not None


def test_default_name_is_id():
    assert (t1 := Transition()).id == t1.name


def test_repr_without_icon():
    t = Transition(name="transition", icon=None)
    assert repr(t) == "transition"

    t = Transition(icon=None)
    assert repr(t).startswith("<Transition")
    assert t.id in repr(t)


def test_sorts_by_name():
    t0 = Transition("C")
    t1 = Transition("B")
    t2 = Transition("A")
    assert list(sorted([t0, t1, t2])) == [t2, t1, t0]


def test_passthrough():
    c0 = Color("0")
    c1 = Color("1")
    t0 = c0()
    t1 = c1()
    fn0 = passthrough(c0)
    fn1 = passthrough({c0})
    fn2 = passthrough({c0: 1}, "invalid-type-will-be-ignored")  # type: ignore
    inputs = {t0, t1}
    expected = s(s(t0))
    assert expected == s(*fn0(inputs)) == s(*fn1(inputs)) == s(*fn2(inputs))

    fn3 = passthrough({c0, c1})
    expected = s(s(t0, t1))
    assert expected == s(*fn3(inputs))

    fn4 = passthrough({c0: 2})
    expected = s()
    assert expected == s(*fn4(inputs))
