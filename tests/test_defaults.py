from carladam.petrinet.defaults import default_id


def test_default_id_is_unique():
    assert default_id() != default_id()
