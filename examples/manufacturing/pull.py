from carladam import PetriNet, Place, Token, Transition, arc, arc_path


class Pull(PetriNet):
    """Manufacturing products using a pull-style workflow."""

    class Structure:
        ready_a = Place()
        prep_a = Transition()
        preparing_a = Place()
        work_a = Transition()
        working_a = Place()
        done_a = Transition()
        product_a = Place()
        demand_a = Place()

        ready_b = Place()
        prep_b = Transition()
        preparing_b = Place()
        work_b = Transition()
        working_b = Place()
        done_b = Transition()
        product_b = Place()
        demand_b = Place()

        ready_c = Place()
        prep_c = Transition()
        preparing_c = Place()
        work_c = Transition()
        working_c = Place()
        done_c = Transition()
        product_c = Place()
        demand_c = Place()

        order_c = Transition()
        receive_c = Transition()
        received = Place()

        arcs = {
            # A
            *arc_path(demand_a, prep_a, preparing_a, work_a, working_a, done_a, product_a),
            *arc_path(done_a, ready_a, prep_a),
            # B
            *arc_path(demand_b, prep_b, preparing_b, work_b, working_b, done_b, product_b),
            *arc_path(done_b, ready_b, prep_b),
            # C
            *arc_path(demand_c, prep_c, preparing_c, work_c, working_c, done_c, product_c),
            *arc_path(done_c, ready_c, prep_c),
            # A<-->B
            arc(prep_b, demand_a),
            arc(product_a, work_b),
            # B<-->C
            arc(prep_c, demand_b),
            arc(product_b, work_c),
            # Ordering and receiving C
            arc(order_c, demand_c),
            *arc_path(product_c, receive_c, received),
        }

        example_markings = {
            "Initialized": {
                ready_a: Token() * 2,
                ready_b: Token() * 3,
                ready_c: Token() * 4,
            },
        }

        clusters = {
            "A": {ready_a, prep_a, preparing_a, work_a, working_a, done_a, product_a, demand_a},
            "B": {ready_b, prep_b, preparing_b, work_b, working_b, done_b, product_b, demand_b},
            "C": {ready_c, prep_c, preparing_c, work_c, working_c, done_c, product_c, demand_c},
            "Ordering": {order_c, receive_c, received},
        }
