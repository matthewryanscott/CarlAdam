from __future__ import annotations

from itertools import repeat
from typing import AbstractSet, Any, Callable, Mapping

from attr import Factory, define, field
from pyrsistent import pmap, pset

from carladam.petrinet.color import Abstract, Color
from carladam.petrinet.defaults import default_id


@define
class Token:
    """A `Token` represents a real or abstract object used to model state of `Place`s and I/O of `Transitions`."""

    id: str = field(factory=default_id, repr=False)
    "Globally unique ID, used as a hash key."

    name: str = field()
    "Descriptive name, usually but not necessarily unique within a net."

    color: Color = Abstract
    "Discrete label describing the kind of this token."

    data: Mapping[str, Any] = Factory(pmap)
    "Arbitrary data attached to the token, potentially used during the `guard` or `fn` of a `Transition`."

    # noinspection PyUnresolvedReferences
    @name.default
    def _default_name_is_id(self):
        """By default, `name` is set to the `id` if not passed in."""
        return self.id

    def replace(self, **kwargs) -> Token:
        """Return a copy of this `Token` but with `data` replaced with `kwargs`."""
        return Token(id=self.id, name=self.name, color=self.color, data=kwargs)

    def clone(self) -> Token:
        """Return a clone of this `Token` but having a new `id` and `name`."""
        return Token(id=default_id(), color=self.color, data=self.data)

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        return (self.color.label, self.name) < (other.color.label, other.name)

    def __mul__(self, quantity: int) -> TokenSet:
        if not isinstance(quantity, int):
            raise TypeError("Can only multiply tokens by integers")
        return frozenset(clone() for clone in repeat(self.clone, quantity))

    def __repr__(self):
        if self.name == self.id:
            s = repr(self.color)
        else:
            s = f"{self.color!r} {self.name}"
        if self.data:
            value_list = [f"{key}={value!r}" for key, value in self.data.items()]
            return f"{s}({', '.join(value_list)})"
        return s


TokenSet = AbstractSet[Token]
"A set of `Token`."

TokenFilter = Callable[[TokenSet], TokenSet]
TokenReducer = Callable[[TokenSet], Token]


def tokens_where(*conditions) -> TokenFilter:
    """
    Return a function that filters a set of tokens to only those that match all conditions given.

    Each condition is a function that takes a token and returns True or False.
    """

    def where_token_filter(tokens: TokenSet) -> TokenSet:
        return pset(token for token in tokens if all(condition(token) for condition in conditions))

    return where_token_filter


def _no_filter(tokens: TokenSet) -> TokenSet:
    return tokens


def one(token_filter: TokenFilter = _no_filter) -> TokenReducer:
    """Return a function taking a set of one token, returning the token or raising `ValueError` if >1 token given."""

    def one_token_reducer(tokens: TokenSet) -> Token:
        tokens = token_filter(tokens)
        if len(tokens) != 1:
            raise ValueError(f"Expected 1 token, got {len(tokens)}")
        return next(iter(tokens))

    return one_token_reducer
