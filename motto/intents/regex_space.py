import json
import os
from hyperon import *
from hyperon.ext import register_atoms
import re


def get_string_value(value):
    if not isinstance(value, str):
        value = repr(value)
    if len(value) > 2 and ("\"" == value[0]) and ("\"" == value[-1]):
        return value[1:-1]
    return value


class RegularExpression:
    def __init__(self, name, patterns, vars_regex=None):
        self.intentName = name
        self.patterns = patterns
        self.vars_regex = vars_regex

    @staticmethod
    def from_json(filepath):
        with open(filepath, "r", encoding='utf-8') as json_file:
            data = json_file.read()
        if data is None:
            return []
        json_list = json.loads(data)
        reg_expressions = []
        for json_dict in json_list:
            reg_expressions.append(RegularExpression(json_dict['intentName'], json_dict['patterns'],
                                                     json_dict["vars_regex"] if "vars_regex" in json_dict else None))
        return reg_expressions


class RegexSpace(GroundingSpace):
    def __init__(self, templates_dir):
        super().__init__()
        templates_dir = get_string_value(templates_dir)
        self.regular_expressions = []
        if os.path.exists(templates_dir):
            for f in os.listdir(templates_dir):
                if f.endswith('.json'):
                    self.load_expressions_from_file(filepath=os.path.join(templates_dir, f))



    def load_expressions_from_file(self, filepath):
        regular_expressions = RegularExpression.from_json(filepath)
        if regular_expressions is not None:
            self.regular_expressions.extend(regular_expressions)

    def var_value_matched(self, vars, vars_regex):
        for k, v in vars.items():
            if k in vars_regex:
                match = re.search(pattern=vars_regex[k], string=v, flags=re.IGNORECASE)
                if match is None:
                    return False
        return True

    def match_text(self, text, regexpr, expr):
        match = re.search(pattern=regexpr, string=text.strip(), flags=re.IGNORECASE)
        if match:
            return {"intent_name": expr.intentName, "match_len": match.end() - match.start()}
        return None

    def query(self, query_atom):
        atoms = query_atom.get_children()
        result = None
        new_bindings_set = BindingsSet.empty()

        if len(atoms) > 1:
            var_to_bind = get_string_value(atoms[0])
            if var_to_bind.find("$") == 0:
                var_to_bind = var_to_bind[1:]

            phrase = atoms[1]
            text = get_string_value(phrase)
            text = ' '.join([x.strip() for x in text.split()])
            max_len = 0
            for expr in self.regular_expressions:
                for pattern in expr.patterns:
                    matched = self.match_text(text, pattern, expr)
                    if matched is not None:
                        if matched["match_len"] > max_len:
                            max_len = matched.pop("match_len")
                            result = matched
            if isinstance(result, dict) and ("intent_name" in result):
                bindings = Bindings()
                bindings.add_var_binding(var_to_bind, ValueAtom(result["intent_name"]))
                new_bindings_set.push(bindings)

        return new_bindings_set


@register_atoms
def regex_space_atoms():
    newRegexSpaceAtom = OperationAtom('new-regex-space', lambda templates_path: [
        G(SpaceRef(RegexSpace(templates_path)))], unwrap=False)

    return {
        r"new-regex-space": newRegexSpaceAtom
    }
