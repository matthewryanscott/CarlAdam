from carladam.petrinet.place import Place


def test_can_be_created():
    Place()


def test_is_hashable():
    p0, p1 = Place(), Place()
    s = {p0, p1}
    s.update({p1})
    assert len(s) == 2


def test_has_auto_assigned_id():
    assert Place().id is not None


def test_default_name_is_id():
    assert (place := Place()).id == place.name


def test_repr_without_icon():
    p = Place(name="place", icon=None)
    assert repr(p) == "place"

    p = Place(icon=None)
    assert repr(p).startswith("<Place")
    assert p.id in repr(p)


def test_sorts_by_name():
    p0 = Place("C")
    p1 = Place("B")
    p2 = Place("A")
    assert list(sorted([p0, p1, p2])) == [p2, p1, p0]
