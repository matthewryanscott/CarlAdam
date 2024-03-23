import pytest

from carladam import autoname
from carladam.petrinet import defaults
from carladam.petrinet.color import Abstract, Color, color_eq
from carladam.petrinet.token import Token, one, tokens_where


def test_can_be_created():
    Token()


def test_is_hashable():
    t0, t1 = Token(), Token()
    s = {t0, t1}
    s.update({t1})
    assert len(s) == 2


def test_has_auto_assigned_id():
    assert Token().id is not None


def test_default_name_is_id():
    assert (token := Token()).id == token.name


def test_default_color_is_abstract():
    t0, t1 = Token(), Token()
    assert t0.color == Abstract
    colors = {t0.color, t1.color}
    assert len(colors) == 1


def test_repr():
    t0 = Token()
    assert repr(t0) == defaults.ABSTRACT_TOKEN

    autoname(t1 := Abstract())
    assert repr(t1) == f"{defaults.ABSTRACT_TOKEN} T1"

    autoname(t2 := Abstract(x=5, y=6))
    assert repr(t2) == f"{defaults.ABSTRACT_TOKEN} T2(x=5, y=6)"


def test_sorts_by_color_then_name():
    c0 = Color("0")
    c1 = Color("1")

    t0 = Token(name="B", color=c0)
    t1 = Token(name="B", color=c1)
    t2 = Token(name="A", color=c1)
    t3 = Token(name="A", color=c0)

    assert list(sorted([t0, t1, t2, t3])) == [t3, t0, t2, t1]


def test_tokens_where():
    c0 = Color("0")
    c1 = Color("1")

    t0a, t0b = c0(), c0()
    t1a, t1b = c1(), c1()

    assert tokens_where(color_eq(c0))({t0a, t0b, t1a, t1b}) == {t0a, t0b}


def test_one():
    t0, t1 = Token(), Token()
    assert one()({t0}) == t0
    with pytest.raises(ValueError):
        one()({t0, t1})


def test_token_multiply():
    tokens = Token(data={"foo": "bar"}) * 3
    assert len(tokens) == 3
    assert all(t.data == {"foo": "bar"} for t in tokens)


@pytest.mark.parametrize("value", [1.2, "string", [], {}, None])
def test_token_multiply_not_int(value):
    with pytest.raises(TypeError):
        Token() * value  # noqa
