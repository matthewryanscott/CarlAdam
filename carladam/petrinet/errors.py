from __future__ import annotations


class PetriNetException(Exception):
    """Base class for all exceptions related to `PetriNet` operations."""


class PetriNetArcIncomplete(PetriNetException):
    """The arc cannot be added because its endpoints are not set."""


class PetriNetTransitionFunctionOutputHasOverlappingColorsets(PetriNetException):
    """The transition cannot occur due to overlapping colorsets of the output tokensets."""


class TransitionNotEnabled(Exception):
    pass


class TransitionHasNoArcs(TransitionNotEnabled):
    pass


class ArcGuardReturnsFalse(TransitionNotEnabled):
    pass


class ArcGuardRaisesException(Exception):
    pass


class TransitionGuardReturnsFalse(TransitionNotEnabled):
    pass


class TransitionGuardRaisesException(Exception):
    pass
