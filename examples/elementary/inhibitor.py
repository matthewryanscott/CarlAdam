from carladam import PetriNet, Place, Token, Transition, arc
from carladam.petrinet.arc import inhibitor_arc


class SimplePetriNetInhibitor(PetriNet):
    """
    Elementary Petri net with inhibitor arcs.
    """

    class Structure:
        class P:
            p0 = Place()
            p1 = Place()

        class T:
            t = Transition()

        arcs = {
            arc(T.t, P.p1),
            inhibitor_arc(P.p0, T.t),
            inhibitor_arc(P.p1, T.t),
        }

        example_markings = {
            "Start here": {
                P.p0: {Token()},
            }
        }


class YesNoInhibitor(PetriNet):
    """
    You can only choose Yes or No once, and the choice depends on input.
    """

    class Structure:
        class P:
            input = Place()
            yes = Place()
            no = Place()

        class T:
            yes = Transition()
            no = Transition()

        arcs = {
            arc(P.input, T.yes),
            arc(T.no, P.no),
            arc(T.yes, P.yes),
            inhibitor_arc(P.input, T.no),
            inhibitor_arc(P.no, T.no),
            inhibitor_arc(P.no, T.yes),
            inhibitor_arc(P.yes, T.no),
            inhibitor_arc(P.yes, T.yes),
        }

        example_markings = {
            "Yes enabled": {
                P.input: {Token()},
            },
            "No enabled": {},
        }
