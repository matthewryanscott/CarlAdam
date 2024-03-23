from carladam import Abstract, Color, PetriNet, Place, Transition

Coin = Color("🪙")
Packet = Color("📦")
Counter = Color("🧮")


def x_minus_1(token):
    return token.replace(x=token.data["x"] - 1)


def counter_x_gt_0(inputs):
    counters = (token for token in inputs if token.color == Counter)
    return all(counter.data["x"] > 0 for counter in counters)


class UnderstandingPetriNetsFigure_1_06(PetriNet):  # noqa
    """
    Understanding Petri Nets: Figure 1.6

    The cookie vending machine with the cold transitions of its interface
    """

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
            insert_coin = Transition(fn=Coin.produce())
            take_packet = Transition()

        arcs = {
            T.insert_coin >> Coin >> P.coin_slot,
            P.coin_slot >> Coin >> T.a,
            T.a >> Coin >> P.cash_box,
            T.a >> P.signal,
            P.signal >> T.b,
            P.storage >> Packet >> T.b,
            T.b >> Packet >> P.compartment,
            P.compartment >> Packet >> T.take_packet,
        }

        clusters = {
            "": {
                T.insert_coin,
                P.coin_slot,
                T.a,
                P.signal,
                T.b,
                P.compartment,
                T.take_packet,
            }
        }

        example_markings = {
            "Start here": {
                P.storage: Packet() * 5,
            },
        }
