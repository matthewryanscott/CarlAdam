from carladam import Abstract, Annotate, Color, PetriNet, Place, TransformEach, Transition

Coin = Color("🪙")
Packet = Color("📦")
Counter = Color("🧮")


def x_minus_1(token):
    return token.replace(x=token.data["x"] - 1)


def counter_x_gt_0(inputs):
    counters = (token for token in inputs if token.color == Counter)
    return all(counter.data["x"] > 0 for counter in counters)


class UnderstandingPetriNetsFigure_1_10_11(PetriNet):  # noqa
    """Understanding Petri Nets: Figures 1.10, 1.11"""

    class Structure:
        class P:
            cash_box = Place()
            coin_slot = Place()
            compartment = Place()
            counter = Place()
            signal = Place()
            storage = Place()

        class T:
            a = Transition(
                guard=counter_x_gt_0,
                annotation="x > 0",
                fn=[Coin.produce(), Abstract.produce(), Counter.passthrough()],
            )
            b = Transition(fn=[Abstract.produce(), Packet.produce()])
            insert_coin = Transition(fn=Coin.produce())
            return_coin = Transition()
            take_packet = Transition()

        arcs = {
            P.coin_slot >> Coin >> T.a,
            P.coin_slot >> Coin >> T.return_coin,
            P.compartment >> Packet >> T.take_packet,
            P.counter >> Counter >> Annotate("x") >> T.a,
            P.signal >> T.b,
            P.storage >> Packet >> T.b,
            T.a >> Coin >> P.cash_box,
            T.a >> Counter >> Annotate("x-1") >> TransformEach(x_minus_1) >> P.counter,
            T.a >> P.signal,
            T.b >> Packet >> P.compartment,
            T.insert_coin >> Coin >> P.coin_slot,
        }

        example_markings = {
            "Figure 1.10: Addition of a counter": {
                P.coin_slot: {Coin()},
                P.counter: {Counter(x=5)},
                P.storage: Packet() * 5,
            },
            "Figure 1.11: After the occurrence of a": {
                P.counter: {Counter(x=4)},
                P.storage: Packet() * 5,
                P.cash_box: {Coin()},
                P.signal: {Abstract()},
            },
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
            },
        }
