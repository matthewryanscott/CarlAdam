# Python imports
import inspect
import typing
from collections import Counter
from typing import Type

# Internal imports
from carladam.petrinet.place import Place
from carladam.petrinet.token import Token
from carladam.petrinet.transition import Transition


AutoNameableTypes = (Place, Token, Transition)
"Types that can be automatically given a name."


AUTONAME_TYPE_COUNTER: typing.Counter[Type] = Counter()


def capitalize(key: str) -> str:
    """Default function used to autoname."""
    return key.replace("_", " ").capitalize()


AUTONAME_ID_SHORTENED = {
    "Place": "P",
    "Transition": "T",
}


def autoname(*objects, set_id=True, autoname_fn=capitalize):
    """
    Auto-name CarlAdam objects wherever possible, based on the calling stack as needed.

    Examples::

        >>> from carladam import *
        >>> my_place = Place()
        >>> my_place  #doctest: +ELLIPSIS
        ⬭ ...
        >>> autoname(my_place)
        ⬭ My place
        >>> my_place
        ⬭ My place

        >>> autoname(my_transition := Transition())
        □ My transition

        >>> net = PetriNet.new(autoname(
        ...     p0 := Place(),
        ...     t0 := Transition(),
        ...     p1 := Place(),
        ...     a0 := p0 >> t0,
        ...     a1 := t0 >> p1,
        ... ))
        >>> a0
        ⬭ P0 → □ T0
    """
    if len(objects) == 1 and isinstance(single_class := objects[0], type):
        # The namespace is a class's attributes.
        # The objects are all of those class's attribute values.
        d = single_class.__dict__
        items = d.items()
        objects = d.values()
        return_value = single_class
    else:
        # The namespace is the calling stack frame.
        # The object(s) are those which were passed in to autoname.
        items = inspect.stack()[1].frame.f_locals.items()
        return_value = objects[0] if len(objects) == 1 else objects

    # Autoname objects that are in the namespace.
    for key, value in items:
        if isinstance(value, type):
            value = autoname(value)
        if key == "_":
            # Always ignore _.
            continue
        if not isinstance(value, AutoNameableTypes):
            # Not a nameable object.
            continue
        if value.name != value.id:
            # Object already given a name.
            continue
        if value not in objects:
            # Did not ask for this object to be autonamed.
            continue

        # Set the new name.
        value.name = autoname_fn(key)

        if set_id:
            # Ensure that other values of this type having this name are given the same ID.
            value_type = type(value)
            value_type_name = value_type.__name__
            value_type_name = AUTONAME_ID_SHORTENED.get(value_type_name, value_type_name)
            AUTONAME_TYPE_COUNTER.update({value_type})
            value.id = f"{value_type_name}{AUTONAME_TYPE_COUNTER[value_type]}{key}"

    return return_value
