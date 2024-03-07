# Internal imports
import carladam as ca


CheeseBlock = ca.Color("🧀")


BREAD_SLICES = 2
CHEESE_SLICES = 3
CHEESE_SLICE_MM = 2


def enough_cheese_left(inputs: ca.TokenSet, slice_mm=CHEESE_SLICE_MM) -> bool:
    cheese_block = ca.one(ca.tokens_where(ca.color_eq(CheeseBlock)))(inputs)
    return cheese_block.data["thickness_mm"] >= slice_mm


def cheese_minus_slice(inputs: ca.TokenSet, slice_mm=CHEESE_SLICE_MM) -> ca.TokenSet:
    cheese_block = ca.one(ca.tokens_where(ca.color_eq(CheeseBlock)))(inputs)
    cheese_block = cheese_block.replace(thickness_mm=cheese_block.data["thickness_mm"] - slice_mm)
    yield {cheese_block}


class MakeCheeseSandwich(ca.PetriNet):
    """How to make a cheese sandwich that you'd like to eat."""

    class Structure(ca.PetriNet.Structure):
        class P:
            bread_slices = ca.Place()
            cheese_block = ca.Place()
            cheese_sandwich = ca.Place()
            cheese_slices = ca.Place()
            edible_bread_slices = ca.Place()
            moldy_bread_slices = ca.Place()

        class T:
            eat_cheese_sandwich = ca.Transition()
            layer_cheese_between_bread = ca.Transition()
            see_mold_on_bread_slice = ca.Transition()
            see_no_mold_on_bread_slice = ca.Transition()
            compost_moldy_bread_slice = ca.Transition()
            slice_cheese = ca.Transition(
                annotation=f"thickness_mm >= {CHEESE_SLICE_MM}",
                guard=enough_cheese_left,
                fn=[ca.Abstract.produce(1), cheese_minus_slice],
            )

        arcs = {
            T.eat_cheese_sandwich << P.cheese_sandwich,
            T.layer_cheese_between_bread << {ca.Abstract: BREAD_SLICES} << P.edible_bread_slices,
            T.layer_cheese_between_bread << {ca.Abstract: CHEESE_SLICES} << P.cheese_slices,
            T.layer_cheese_between_bread >> P.cheese_sandwich,
            T.see_mold_on_bread_slice << P.bread_slices,
            T.see_mold_on_bread_slice >> P.moldy_bread_slices,
            T.see_no_mold_on_bread_slice << P.bread_slices,
            T.see_no_mold_on_bread_slice >> P.edible_bread_slices,
            T.compost_moldy_bread_slice << P.moldy_bread_slices,
            T.slice_cheese << CheeseBlock << P.cheese_block << ca.Annotate("thickness_mm"),
            T.slice_cheese >> CheeseBlock >> P.cheese_block >> ca.Annotate(f"thickness_mm - {CHEESE_SLICE_MM}"),
            T.slice_cheese >> P.cheese_slices,
        }

        example_markings = {
            "Full pantry": {
                P.bread_slices: {ca.Abstract() for _ in range(10)},
                P.cheese_block: {CheeseBlock(thickness_mm=100)},
            },
        }

        clusters = {
            "Bread inspection": {
                P.bread_slices,
                T.see_no_mold_on_bread_slice,
                T.see_mold_on_bread_slice,
                P.moldy_bread_slices,
                P.edible_bread_slices,
                T.compost_moldy_bread_slice,
            },
            "Slice cheese": {
                P.cheese_block,
                T.slice_cheese,
                P.cheese_slices,
            },
            "The final stretch": {
                P.edible_bread_slices,
                P.cheese_slices,
                P.cheese_sandwich,
                T.layer_cheese_between_bread,
                T.eat_cheese_sandwich,
            },
        }
