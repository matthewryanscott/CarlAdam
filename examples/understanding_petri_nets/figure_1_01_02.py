from carladam import Color, PetriNet, Place, Transition

Coin = Color("🪙")
Packet = Color("📦")


class UnderstandingPetriNetsFigure_1_01_02(PetriNet):  # noqa
    """Understanding Petri Nets: Figures 1.1, 1.2"""

    class Structure:
        class P:
            coin_slot = Place()
            compartment = Place()

        class T:
            t = Transition(fn=[Packet.produce()])

        arcs = {
            P.coin_slot >> Coin >> T.t,
            T.t >> Packet >> P.compartment,
        }

        example_markings = {
            "Figure 1.1: The cookie vending machine in its initial state": {
                P.coin_slot: {Coin()},
            },
            "Figure 1.2: The cookie vending machine after the occurrence of t": {
                P.compartment: {Packet()},
            },
        }
