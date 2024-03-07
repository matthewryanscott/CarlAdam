from __future__ import annotations

# Python imports
from collections import Counter
from typing import AbstractSet, Mapping, MutableMapping

# Pip imports
from pyrsistent import pmap, pset
from pyrsistent.typing import PMap as PMapType
from pyrsistent.typing import PSet as PSetType

# Internal imports
from carladam.petrinet.color import ColorSet
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token


Marking = Mapping[Place, AbstractSet[Token]]
"A mapping between `Place`s and their respective `Token`s."

MutableMarking = MutableMapping[Place, AbstractSet[Token]]

PMarking = PMapType[Place, PSetType[Token]]


def marking_colorset(marking: Marking) -> Mapping[Place, ColorSet]:
    """
    Transforms a `Marking` into the quantities of tokens (grouped by color) for each `Place`.

    Empty places are not included in the return value.
    This ensures brevity in unit tests when comparing with expected values.
    """
    return pmap((place, pmap(Counter(token.color for token in tokens))) for place, tokens in marking.items() if tokens)


def pmarking(marking: Marking | MutableMarking | PMarking) -> PMarking:
    """Returns an immutable marking given a mutable or immutable marking."""
    return pmap((place, pset(tokens)) for place, tokens in marking.items())
