from hyperon import *
from hyperon.ext import register_tokens
import re


def get_string_value(value) -> str:
    if not isinstance(value, str):
        value = repr(value)
    if len(value) > 2 and ("\"" == value[0]) and ("\"" == value[-1]):
        return value[1:-1]
    return value


class RegexMatchableObject(MatchableObject):
    def __init__(self, content, id=None):
        super().__init__(content, id)

        """Initializes a new GroundedObject with the given content and identifier."""
        self.content = self.content.replace("[[", "(").replace("]]", ")")

    def match_text(self, text, regexpr):
        return re.search(pattern=regexpr, string=text.strip(), flags=re.IGNORECASE)

    def match_(self, atom):
        pattern = self.content
        text = get_string_value(atom)
        text = ' '.join([x.strip() for x in text.split()])
        if pattern.startswith("regex:"):
            pattern = get_string_value(pattern[6:])
            matched = self.match_text(text, pattern)
            if matched is not None:
                return [{"matched_pattern": S(pattern)}]
        return []


def RegexMatchableAtom(value, type_name=None, atom_id=None):
    return G(RegexMatchableObject(value, atom_id), AtomType.UNDEFINED)


@register_tokens
def regex_token():
    return {
        'regex:[^\s]+': lambda token: RegexMatchableAtom(token)
    }
