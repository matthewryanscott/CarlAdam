from carladam import PetriNet, Place, Token, Transition
from carladam.petrinet.arc import arc


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
            arc(P.p0, T.t),
            arc(T.t, P.p1),
        }
        example_markings = {
            "Start here": {
                P.p0: {Token()},
            }
        }
