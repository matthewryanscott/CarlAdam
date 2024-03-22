from carladam import Abstract, Color, PetriNet, Place, Transition
from carladam.petrinet.marking import marking_colorset

Coin = Color("🪙")
Packet = Color("📦")


def test_figure_1_3():
    # noinspection PyPep8Naming
    class Figure_1_3(PetriNet):
        class Structure:
            class P:
                cash_box = Place()
                coin_slot = Place()
                compartment = Place()
                signal = Place()
                storage = Place()

            class T:
                a = Transition(fn=[Coin.produce(), Abstract.produce()])
                b = Transition(fn=Packet.produce())

            arcs = {
                P.coin_slot >> Coin >> T.a,
                P.signal >> T.b,
                P.storage >> Packet >> T.b,
                T.a >> Coin >> P.cash_box,
                T.a >> P.signal,
                T.b >> Packet >> P.compartment,
            }

    figure_1_3 = Figure_1_3.new()
    s = figure_1_3.structure

    m0 = {
        s.P.coin_slot: {Coin()},
        s.P.storage: {Packet(), Packet(), Packet(), Packet(), Packet()},
    }

    m1 = figure_1_3.marking_after_transition(m0, s.T.a)
    assert marking_colorset(m1) == {
        s.P.cash_box: {Coin: 1},
        s.P.signal: {Abstract: 1},
        s.P.storage: {Packet: 5},
    }

    m2 = figure_1_3.marking_after_transition(m1, s.T.b)
    assert marking_colorset(m2) == {
        s.P.cash_box: {Coin: 1},
        s.P.storage: {Packet: 4},
        s.P.compartment: {Packet: 1},
    }
