from carladam import Abstract, Color, PetriNet, Place, Transition

Coin = Color("🪙")
Packet = Color("📦")
Counter = Color("🧮")


def x_minus_1(token):
    return token.replace(x=token.data["x"] - 1)


def counter_x_gt_0(inputs):
    counters = (token for token in inputs if token.color == Counter)
    return all(counter.data["x"] > 0 for counter in counters)


class UnderstandingPetriNetsFigure_1_07_08_09(PetriNet):  # noqa
    """
    Understanding Petri Nets: Figures 1.7, 1.8, 1.9

    The cookie vending machine with the option of returning coins.
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
            return_coin = Transition()

        arcs = {
            T.insert_coin >> Coin >> P.coin_slot,
            P.coin_slot >> Coin >> T.return_coin,
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
            "Figure 1.7: The cookie vending machine with the option of returning coins": {
                P.storage: Packet() * 5,
            },
            "Figure 1.8: Two options: `return coin` and `a`": {
                P.coin_slot: {Coin()},
                P.storage: Packet() * 5,
            },
            "Figure 1.9: Reachable marking of the cookie vending machine": {
                P.cash_box: Coin() * 5,
                P.signal: {Abstract()},
            },
        }
