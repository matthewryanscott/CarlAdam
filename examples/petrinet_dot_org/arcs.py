from carladam import Abstract, PetriNet, Place, Transition


class PetriNetDotOrgArcs(PetriNet):
    """
    Arcs

    See [petrinet.org/#Arcs](http://petrinet.org/#Arcs)
    """

    class Structure:
        class P:
            storage = Place()
            customer_a = Place()
            customer_b = Place()

        class T:
            create = Transition()
            distribute = Transition()
            consume_a = Transition()
            consume_b = Transition()

        arcs = {
            P.customer_a >> T.consume_a,
            P.customer_b >> T.consume_b,
            P.storage >> {Abstract: 2} >> T.distribute,
            T.create >> P.storage,
            T.distribute >> P.customer_a,
            T.distribute >> P.customer_b,
        }
