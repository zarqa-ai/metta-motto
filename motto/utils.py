import os
import sys

from hyperon.atoms import OperationAtom, OperationObject, ValueAtom, SymbolAtom, \
    ValueObject
from hyperon.ext import register_atoms


def get_string_value(atom) -> str:
    item = repr(atom)
    if len(item) > 2 and ((item[0] == '"' and item[-1] == '"') or (item[0] == "'" and item[-1] == "'")):
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


def create_array(*atoms):
    if len(atoms) > 0:
        return  [ValueAtom([atom.get_object().content for atom in atoms])]
    return []


def create_dict(*atoms):
    if len(atoms) > 0:
        res_dict = {}
        for atom in atoms:
            try:
                items = atom.get_children()
                assert len(items) == 2
                key = items[0].get_object().content if hasattr(items[0], 'get_object') else get_string_value(items[0])
                value = items[1].get_object().content if hasattr(items[1], 'get_object') else get_string_value(items[1])
                res_dict[key] = value
            except Exception as e:
                raise RuntimeError(f"Incorrect dictionary items format {atom} : {e}")
        return [ValueAtom(res_dict)]
    return []


@register_atoms(pass_metta=True)
def reg_py_imports(metta):
    return {r'py-array': OperationAtom('py-array', create_array, unwrap=False),
            r'py-dict': OperationAtom('py-dict', create_dict, unwrap=False), }
