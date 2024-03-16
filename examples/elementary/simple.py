# Internal imports
from carladam import PetriNet, Place, Token, Transition


def inhibitor(arc, tokens):
    return not tokens


class SimplePetriNet(PetriNet):
    """
    Elementary Petri net

    There is only one transition active.
    """

    class Structure:
        class P:
            p0 = Place()
            p1 = Place()

        class T:
            t = Transition()

        arcs = {
            P.p0 >> T.t,
            T.t >> P.p1,
        }

        example_markings = {
            "Start here": {
                P.p0: {Token()},
            }
        }


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
            (P.p0 >> T.t)(annotation="⃝", guard=inhibitor),
            (P.p1 >> T.t)(annotation="⃝", guard=inhibitor),
            T.t >> P.p1,
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
            P.input >> T.yes,
            (P.input >> T.no)(guard=inhibitor),
            (P.no >> T.no)(annotation="⃝", guard=inhibitor),
            (P.yes >> T.no)(annotation="⃝", guard=inhibitor),
            (P.no >> T.yes)(annotation="⃝", guard=inhibitor),
            (P.yes >> T.yes)(annotation="⃝", guard=inhibitor),
            T.yes >> P.yes,
            T.no >> P.no,
        }

        example_markings = {
            "Yes enabled": {
                P.input: {Token()},
            },
            "No enabled": {},
        }
