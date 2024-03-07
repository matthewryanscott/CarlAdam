# Pip imports
from pyrsistent import pmap, s

# Internal imports
from carladam import Place, Token
from carladam.petrinet.marking import pmarking


def test_pmarking():
    p = Place()
    token = Token()
    dict_marking = {p: {token}}
    expected_pmarking = pmap().set(p, s(token))
    assert pmarking(dict_marking) == expected_pmarking
    assert type(pmarking(dict_marking)) == type(expected_pmarking)
    assert pmarking(expected_pmarking) == expected_pmarking
