# Python imports
from typing import Iterable, Union

# Internal imports
from carladam.petrinet.arc import ArcPT, ArcTP, CompletedArcPT, CompletedArcTP
from carladam.petrinet.place import Place
from carladam.petrinet.transition import Transition


Arc = Union[ArcPT, ArcTP]
"Union of arc types, used for type annotation."

CompletedArc = Union[CompletedArcPT, CompletedArcTP]
"Union of completed arc types, used for type annotation."

ArcTypes = (ArcPT, ArcTP)
"Tuple of arc types, used for `isinstance` checking."

CompletedArcTypes = (CompletedArcPT, CompletedArcTP)
"Tuple of completed arc types, used for `isinstance` checking."

PetriNetMember = Union[Place, Transition, Arc]
"Object which can be a member of a `PetriNet`."

PetriNetMemberSet = Iterable[PetriNetMember]
"Iterable of objects which can be members of a `PetriNet`."

PetriNetMemberOrSet = Union[PetriNetMember, PetriNetMemberSet]
"Object or iterable of objects which can be members of a `PetriNet`."

PetriNetNode = Union[Place, Transition]
"Object that is a node in a `PetriNet`."
