import os
import sys
from hyperon import *


def get_string_value(atom) -> str:
    item = repr(atom)
    if len(item) > 2 and (item[0] == '"' and item[-1] == '"'):
        item = item[1:-1]
    return item


def contains_str(value, substring) -> bool:
    str1 = get_string_value(value)
    substring = get_string_value(substring)
    return substring.lower() in str1.lower()


def concat_str(left, right) -> str:
    str1 = get_string_value(left)
    str2 = get_string_value(right)
    return str1 + str2


def process_inner(inner_children):
    if len(inner_children) == 2:
        return (get_string_value(inner_children[0]), get_string_value(inner_children[1]))
    raise ValueError()


def message2tuple(msg_atom):
    messages = []
    if hasattr(msg_atom, 'get_children'):
        children = msg_atom.get_children()
        if (len(children) > 1) and repr(children[0]) == "Messages":
            for ch in children[1:]:
                if hasattr(ch, 'get_children'):
                    inner_children = ch.get_children()
                    messages.append(process_inner(inner_children))
        else:
            messages.append(process_inner(children))
    return messages
