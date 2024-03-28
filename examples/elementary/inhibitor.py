from carladam import PetriNet, Place, Token, Transition, arc
from carladam.petrinet.arc import inhibitor_arc


class SimplePetriNetInhibitor(PetriNet):
    """
    Elementary Petri net with inhibitor arcs.
    """

    class Structure:
        p0 = Place()
        p1 = Place()

        t = Transition()

        arcs = {
            arc(t, p1),
            inhibitor_arc(p0, t),
            inhibitor_arc(p1, t),
        }

        example_markings = {
            "Start here": {
                p0: {Token()},
            }
        }


class YesNoInhibitor(PetriNet):
    """
    You can only choose Yes or No once, and the choice depends on input.
    """

    class Structure:
        input = Place()
        yes_chosen = Place()
        no_chosen = Place()

        yes = Transition()
        no = Transition()

        arcs = {
            arc(input, yes),
            arc(yes, yes_chosen),
            inhibitor_arc(input, no),
            inhibitor_arc(yes_chosen, no),
            inhibitor_arc(yes_chosen, yes),
            arc(no, no_chosen),
            inhibitor_arc(no_chosen, no),
            inhibitor_arc(no_chosen, yes),
        }

        example_markings = {
            "Yes enabled": {
                input: {Token()},
            },
            "No enabled": {},
        }
