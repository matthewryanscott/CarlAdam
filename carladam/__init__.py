"""
CarlAdam models Petri nets in Python.

This top-level module exports commonly used classes and functions.
"""

from carladam.petrinet.arc import Annotate, TransformEach, arc
from carladam.petrinet.color import Abstract, Color, color_eq
from carladam.petrinet.marking import Marking
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token, TokenSet, one, tokens_where
from carladam.petrinet.transition import Transition, passthrough
from carladam.util.autoname import autoname

__ = autoname
"Convenience alias for `autoname` to reduce noise in notebook cells."

__all__ = [
    "Abstract",
    "Annotate",
    "Color",
    "Marking",
    "PetriNet",
    "Place",
    "Token",
    "TokenSet",
    "TransformEach",
    "Transition",
    "__",
    "arc",
    "autoname",
    "color_eq",
    "one",
    "passthrough",
    "tokens_where",
]
