from carladam import Abstract, Color, PetriNet, Place, Transition

Coin = Color("🪙")
Packet = Color("📦")
Counter = Color("🧮")


def x_minus_1(token):
    return token.replace(x=token.data["x"] - 1)


def counter_x_gt_0(inputs):
    counters = (token for token in inputs if token.color == Counter)
    return all(counter.data["x"] > 0 for counter in counters)


class UnderstandingPetriNetsFigure_1_03_04_05(PetriNet):  # noqa
    """Understanding Petri Nets: Figures 1.3, 1.4, 1.5"""

    class Structure:
        class P:
            cash_box = Place()
            coin_slot = Place()
            compartment = Place()
            signal = Place()
            storage = Place()

        class T:
            a = Transition(fn=[Coin.passthrough(), Abstract.produce()])
            b = Transition(fn=Packet.produce())

        arcs = {
            P.coin_slot >> Coin >> T.a,
            T.a >> Coin >> P.cash_box,
            T.a >> P.signal,
            P.signal >> T.b,
            P.storage >> Packet >> T.b,
            T.b >> Packet >> P.compartment,
        }

        example_markings = {
            "Figure 1.3: A look inside the cookie vending machine": {
                P.coin_slot: {Coin()},
                P.storage: Packet() * 5,
            },
            "Figure 1.4: After the occurrence of a": {
                P.signal: {Abstract()},
                P.storage: Packet() * 5,
            },
            "Figure 1.5: After the occurrence of b": {
                P.compartment: {Packet()},
                P.storage: Packet() * 5,
            },
        }

        clusters = {
            "": {
                P.coin_slot,
                T.a,
                P.signal,
                T.b,
                P.compartment,
            }
        }
