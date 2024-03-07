# Internal imports
from carladam.petrinet.color import Abstract, Color, color_eq, colorset_string


def test_repr_is_name():
    assert Abstract.label == repr(Abstract)
    assert repr(Color("abc")) == "abc"


A = Color("A")
B = Color("B")
C = Color("C")


def test_colorset_string():
    colorset = {C: 3, B: 2, A: 1}
    expected = "ABBCCC"
    assert colorset_string(colorset) == expected


def test_color_eq():
    abstract_token = Abstract()
    non_abstract_token = Color("abc")()
    comparator = color_eq(Abstract)
    assert comparator(abstract_token) is True
    assert comparator(non_abstract_token) is False
