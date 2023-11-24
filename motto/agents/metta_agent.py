from .agent import Agent, Response
from hyperon import MeTTa, ExpressionAtom, E, S

class MettaAgent(Agent):

    def __init__(self, metta, path):
        self._metta = metta
        self._script = path

    def __call__(self, msgs_atom, functions):
        # FIXME: we cannot use top-level self._metta here, because its space
        # will be polluted. Thus, we create new metta runner and import motto.
        # We could avoid importing motto each time by reusing tokenizer or by
        # swapping its space with a temporary space, but current API is not enough.
        # It could also be possible to import! the agent script into a new space,
        # but there is no function to do this without creating a new token
        # (which might be useful). The latter solution will work differently.
        metta = MeTTa()
        metta.run("!(extend-py! motto)")
        metta.space().add_atom(E(S('='), E(S('messages')), msgs_atom))
        response = metta.import_file(self._script)
        # TODO: multiple alternatives for responses
        for rs in response:
            for r in rs:
                if isinstance(r, ExpressionAtom):
                    ch = r.get_children()
                    if len(ch) == 0:
                        continue
                    # TODO: do we always expect a string as a response?
                    return Response(ch[1].get_object().value, None)
        return Response(None, None)
