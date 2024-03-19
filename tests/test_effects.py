from carladam import Abstract, Place, Transition
from carladam.petrinet.effects import Consume, Input, Output, Produce
from carladam.petrinet.marking import pmarking


def test_consume_place_will_have_remaining_token():
    # Given: a place, a transition, and an arc from the place to the transition
    p = Place()
    t = Transition()
    arc = p >> t

    # And: a marking with a token
    token = Abstract()
    token2 = Abstract()
    marking = pmarking({p: {token, token2}})

    # And: an effect indicating that a token was consumed
    effect = Consume(arc, token2)

    # When: the effect is applied to the marking
    marking_after_effect = effect.apply_to_marking(marking)

    # Then: the token is removed from the place
    expected = pmarking({p: {token}})
    assert marking_after_effect == expected


def test_consume_place_will_be_empty():
    # Given: a place, a transition, and an arc from the place to the transition
    p = Place()
    t = Transition()
    arc = p >> t

    # And: a marking with a token
    token = Abstract()
    marking = pmarking({p: {token}})

    # And: an effect indicating that the token was consumed
    effect = Consume(arc, token)

    # When: the effect is applied to the marking
    marking_after_effect = effect.apply_to_marking(marking)

    # Then: the token is removed from the place
    expected = pmarking({})
    assert marking_after_effect == expected


def test_input():
    # Given: a place, a transition, and an arc from the place to the transition
    p = Place()
    t = Transition()
    arc = p >> t

    # And: a marking with a token
    token = Abstract()
    marking = pmarking({p: {token}})

    # And: an effect indicating that the token was used as input for a transition
    effect = Input(arc, token)

    # When: the effect is applied to the marking
    marking_after_effect = effect.apply_to_marking(marking)

    # Then: no changes to the marking are made
    #  (Input effects only model the outputs of a transition after any arc transform, not changes to the pre-set)
    assert marking_after_effect == marking


def test_output():
    # Given: a transition, a place, and an arc from the transition to the place
    t = Transition()
    p = Place()
    arc = t >> p

    # And: a marking where the place has a token
    token = Abstract()
    marking = pmarking({p: {token}})

    # And: an effect indicating that another token was produced as output from a transition
    token2 = Abstract()
    effect = Output(arc, token2)

    # When: the effect is applied to the marking
    marking_after_effect = effect.apply_to_marking(marking)

    # Then: no changes to the marking are made
    #  (Output effects only model the outputs of a transition before any arc transform, not changes to the post-set)
    assert marking_after_effect == marking


def test_produce_place_is_not_empty():
    # Given: a transition, a place, and an arc from the transition to the place
    t = Transition()
    p = Place()
    arc = t >> p

    # And: a marking where the place has a token
    token = Abstract()
    marking = pmarking({p: {token}})

    # And: an effect indicating that another token was produced as output from a transition
    token2 = Abstract()
    effect = Produce(arc, token2)

    # When: the effect is applied to the marking
    marking_after_effect = effect.apply_to_marking(marking)

    # Then: the token is added to the place
    expected = pmarking({p: {token, token2}})
    assert marking_after_effect == expected


def test_produce_place_is_empty():
    # Given: a transition, a place, and an arc from the transition to the place
    t = Transition()
    p = Place()
    arc = t >> p

    # And: an empty marking
    marking = pmarking({})

    # And: an effect indicating that another token was produced as output from a transition
    token = Abstract()
    effect = Produce(arc, token)

    # When: the effect is applied to the marking
    marking_after_effect = effect.apply_to_marking(marking)

    # Then: the token is added to the place
    expected = pmarking({p: {token}})
    assert marking_after_effect == expected
