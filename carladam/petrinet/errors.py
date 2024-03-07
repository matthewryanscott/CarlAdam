class PetriNetException(Exception):
    """Base class for all exceptions related to `PetriNet` operations."""


class PetriNetArcIncomplete(PetriNetException):
    """The arc cannot be added because its endpoints are not set."""


class PetriNetTransitionNotEnabled(PetriNetException):
    """The transition cannot occur because it is not enabled."""


class PetriNetTransitionFunctionOutputHasOverlappingColorsets(PetriNetException):
    """The transition cannot occur due to overlapping colorsets of the output tokensets."""
