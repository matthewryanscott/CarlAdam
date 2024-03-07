# Internal imports
from carladam import PetriNet, Place, Token, Transition


class PetriNetDotOrgIntro(PetriNet):
    """
    Intro

    See [petrinet.org/#Intro](http://petrinet.org/#Intro)
    """

    class Structure:
        class P:
            place_a = Place()
            place_b = Place()
            place_c = Place()
            place_d = Place()

        class T:
            transition_1 = Transition()
            transition_2 = Transition()
            transition_3 = Transition()
            transition_4 = Transition()

        arcs = {
            P.place_a >> T.transition_1,
            P.place_b >> T.transition_2,
            P.place_c >> T.transition_3,
            P.place_d >> T.transition_4,
            T.transition_1 >> P.place_b,
            T.transition_2 >> P.place_c,
            T.transition_3 >> P.place_d,
            T.transition_4 >> P.place_a,
        }

        example_markings = {
            "Initial marking": {
                P.place_a: {Token()},
                P.place_b: {Token()},
            }
        }
