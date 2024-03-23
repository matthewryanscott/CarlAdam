import pytest

from carladam import arc
from carladam.petrinet.color import Color
from carladam.petrinet.marking import Marking, marking_colorset
from carladam.petrinet.petrinet import PetriNet
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token
from carladam.petrinet.transition import Transition

Invoice = Color("🧾")


class InvoiceNet(PetriNet):
    class Structure:
        class P:
            has_vendor = Place()
            has_amount = Place()
            invoice_in_draft = Place()
            approval_pending = Place()
            destination_pending = Place()
            approved = Place()
            destination_account = Place()
            origin_account = Place()
            invoice_posted = Place()
            balance_due = Place()

        class T:
            create_invoice = Transition(fn=Invoice.produce())
            post_invoice = Transition(fn=Invoice.passthrough())
            approve = Transition(fn=Invoice.passthrough())
            define_vendor_account = Transition(fn=Invoice.passthrough())
            create_payment_order = Transition(fn=Invoice.passthrough())

        # Arcs
        arcs = {
            arc(P.approval_pending, T.approve, Invoice),
            arc(P.approved, T.create_payment_order, Invoice),
            arc(P.destination_account, T.create_payment_order, Invoice),
            arc(P.destination_pending, T.define_vendor_account, Invoice),
            arc(P.has_amount, T.post_invoice, Invoice),
            arc(P.has_vendor, T.post_invoice, Invoice),
            arc(P.invoice_in_draft, T.post_invoice, Invoice),
            arc(P.invoice_posted, T.create_payment_order, Invoice),
            arc(P.origin_account, T.create_payment_order, Invoice),
            arc(T.approve, P.approved, Invoice),
            arc(T.create_invoice, P.has_amount, Invoice),
            arc(T.create_invoice, P.has_vendor, Invoice),
            arc(T.create_invoice, P.invoice_in_draft, Invoice),
            arc(T.create_payment_order, P.balance_due, Invoice),
            arc(T.define_vendor_account, P.destination_account, Invoice),
            arc(T.post_invoice, P.approval_pending, Invoice),
            arc(T.post_invoice, P.destination_pending, Invoice),
            arc(T.post_invoice, P.invoice_posted, Invoice),
            arc(T.post_invoice, P.origin_account, Invoice),
        }


@pytest.fixture
def net():
    return InvoiceNet.new()


@pytest.fixture
def s(net) -> InvoiceNet.Structure:
    return net.structure


def test_definition(net, s):
    assert net.transition_is_external(s.T.create_invoice)
    assert not net.transition_is_external(s.T.post_invoice)
    assert not net.transition_is_external(s.T.approve)
    assert not net.transition_is_external(s.T.define_vendor_account)
    assert not net.transition_is_external(s.T.create_payment_order)


def test_enabled_transitions(net, s):
    marking: Marking = {}
    enabled_transitions = set(net.enabled_transitions(marking))
    assert enabled_transitions == {s.T.create_invoice}

    invoice = Token(color=Invoice)
    marking: Marking = {
        s.P.has_vendor: {invoice},
        s.P.has_amount: {invoice},
        s.P.invoice_in_draft: {invoice},
    }
    enabled_transitions = set(net.enabled_transitions(marking))
    assert enabled_transitions == {s.T.create_invoice, s.T.post_invoice}


def test_fire_transitions(net, s):
    m0: Marking = net.empty_marking()

    m1 = net.marking_after_transition(m0, s.T.create_invoice)
    m1_counts = marking_colorset(m1)
    expected_m1_counts = {
        s.P.has_vendor: {Invoice: 1},
        s.P.has_amount: {Invoice: 1},
        s.P.invoice_in_draft: {Invoice: 1},
    }
    assert m1_counts == expected_m1_counts

    m2 = net.marking_after_transition(m1, s.T.post_invoice)
    m2_counts = marking_colorset(m2)
    expected_m2_counts = {
        s.P.origin_account: {Invoice: 1},
        s.P.invoice_posted: {Invoice: 1},
        s.P.approval_pending: {Invoice: 1},
        s.P.destination_pending: {Invoice: 1},
    }
    assert m2_counts == expected_m2_counts
