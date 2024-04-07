import os
import sys

from hyperon.atoms import OperationAtom, OperationObject, ValueAtom, SymbolAtom, \
    ValueObject
from hyperon.ext import register_atoms


def get_string_value(atom) -> str:
    item = repr(atom)
    if len(item) > 2 and item[0] == '"' and item[-1] == '"':
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


def groundedatom_to_python_object(a):
    if isinstance(a, SymbolAtom):
        return repr(a)
    obj = a.get_object()
    if isinstance(obj, ValueObject):
        obj = obj.value
    if isinstance(obj, OperationObject):
        obj = obj.content
    # At this point it is already python object
    return obj


def _import_and_wrap(metta, import_str, obj):
    # we only need these 3 lines to import from the current directory
    # TODO fix it somehow differently
    current_directory = os.getcwd()
    if current_directory not in sys.path:
        sys.path.append(current_directory)

    local_scope = {}
    exec(import_str, {}, local_scope)
    oatom = ValueAtom(local_scope[obj])
    metta.register_atom(obj, oatom)


def import_from(metta, lib, i, obj):
    if str(i) != "import":
        raise Exception("bad import syntax")
    lib = str(lib)
    obj = str(obj)
    _import_and_wrap(metta, f"from {lib} import {obj}", obj)
    return []


def call_function(expression_atom, parameters):
    if isinstance(parameters, dict):
        return expression_atom(**parameters) if len(parameters) > 0 else expression_atom()
    else:
        return expression_atom(**parameters)


def run_python_code_inner(expression_atom, parameters={}):
    if hasattr(expression_atom, "get_children"):
        atoms = expression_atom.get_children()
        first = groundedatom_to_python_object(atoms[0])
        if not callable(first) and len(atoms) == 2:
            parameters.update({first: run_python_code_inner(atoms[1], {})})
        elif callable(first):
            parameters = {}
            for atom in atoms[1:]:
                run_python_code_inner(atom, parameters)
            return call_function(first, parameters)
        else:
            raise Exception("incorrect call of python function")
    else:
        first = groundedatom_to_python_object(expression_atom)
        if callable(first):
            return call_function(first, parameters)
        return first


def run_python_code(expression_atom):
    result = run_python_code_inner(expression_atom, {})
    return [ValueAtom(result)]


@register_atoms(pass_metta=True)
def reg_py_imports(metta):
    return {r'import-from': OperationAtom('import-from', lambda *args: import_from(metta, *args), unwrap=False),
            r'run-py': OperationAtom('run-py', run_python_code, unwrap=False)}