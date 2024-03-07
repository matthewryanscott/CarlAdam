# Internal imports
from carladam import PetriNet, Place, Token, Transition


class PetriNetDotOrgPawelsNet(PetriNet):
    """
    Pawel's Net

    See [petrinet.org/#PawelsNet](http://petrinet.org/#PawelsNet)
    """

    class Structure:
        class P:
            p0 = Place()
            p1 = Place()
            p2 = Place()
            p3 = Place()
            p4 = Place()
            p5 = Place()
            p6 = Place()
            p7 = Place()

        class T:
            t0 = Transition()
            t1 = Transition()
            t2 = Transition()
            t3 = Transition()
            t4 = Transition()

        arcs = {
            P.p0 >> T.t1,
            P.p1 >> T.t2,
            P.p2 >> T.t3,
            P.p3 >> T.t4,
            P.p4 >> T.t0,
            P.p5 >> T.t1,
            P.p6 >> T.t2,
            P.p7 >> T.t3,
            T.t0 >> P.p0,
            T.t1 >> P.p1,
            T.t1 >> P.p4,
            T.t2 >> P.p2,
            T.t2 >> P.p5,
            T.t3 >> P.p3,
            T.t3 >> P.p6,
            T.t4 >> P.p7,
        }

        example_markings = {
            "Initial marking": {
                P.p0: {Token()},
                P.p1: {Token()},
                P.p2: {Token()},
                P.p3: {Token()},
            }
        }
