from .agent import Agent, Response
from hyperon import MeTTa, ExpressionAtom, OperationAtom, E, S

class MettaAgent(Agent):

    def _try_unwrap(self, val):
        if val is None or isinstance(val, str):
            return val
        return repr(val)

    def __init__(self, path=None, code=None, atoms={}):
        self._path = self._try_unwrap(path)
        self._code = self._try_unwrap(code)
        if path is None and code is None:
            raise RuntimeError(f"{self.__class__.__name__} requires either path or code")
        self._atoms = atoms

    def _prepare(self, metta, msgs_atom):
        for k, v in self._atoms.items():
            metta.register_atom(k, v)
        # FIXME: We add this function here, so we can explicitly evaluate results of LLMs, but
        # we may either expect that this function appear in core MeTTa or need a special safe eval
        metta.register_atom("_eval", OperationAtom("_eval",
            lambda atom: metta.run("! " + atom.get_object().value)[0],
            unwrap=False))
        metta.space().add_atom(E(S('='), E(S('messages')), msgs_atom))

    def _postproc(self, response):
        results = []
        # Multiple responses are now returned as a list
        for rs in response:
            for r in rs:
                if isinstance(r, ExpressionAtom):
                    ch = r.get_children()
                    if len(ch) == 0:
                        continue
                    # FIXME? we can simply ignore all non-Response results
                    if len(ch) != 2 or repr(ch[0]) != 'Response':
                        raise TypeError(f"Unexpected response format {ch}")
                    results += [ch[1]]
        return Response(results, None)

    def __call__(self, msgs_atom, functions=[]):
        # FIXME: we cannot use higher-level metta here (e.g. passed by llm func),
        # from which an agent can be called, because its space will be polluted.
        # Thus, we create new metta runner and import motto.
        # We could avoid importing motto each time by reusing tokenizer or by
        # swapping its space with a temporary space, but current API is not enough.
        # It could also be possible to import! the agent script into a new space,
        # but there is no function to do this without creating a new token
        # (which might be useful). The latter solution will work differently.
        metta = MeTTa()
        metta.run("!(extend-py! motto)")
        # TODO: support {'role': , 'content': } dict input
        if isinstance(msgs_atom, str):
            msgs_atom = metta.parse_single(msgs_atom)
        self._prepare(metta, msgs_atom)
        if self._path is not None:
            response = metta.import_file(self._path)
        if self._code is not None:
            response = metta.run(self._code)
        return self._postproc(response)


class DialogAgent(MettaAgent):

    def __init__(self, path = None, code = None):
        self.history = []
        super().__init__(path, code)

    def _prepare(self, metta, msgs_atom):
        super()._prepare(metta, msgs_atom)
        metta.space().add_atom(E(S('='), E(S('history')),
                                 E(S('Messages'), *self.history)))
        # atm, we put the input message into the history by default
        self.history += [msgs_atom]

    def _postproc(self, response):
        # TODO it's very initial version of post-processing
        # The output is added to the history as the assistant utterance.
        # This might be ok: if someone wants to avoid this, Function
        # (TODO not supported yet) instead of Response could be used.
        # But one can add explicit commands for putting something into
        # the history as well as to do other stuff
        result = super()._postproc(response)
        # TODO: 0 or >1 results, to expression?
        self.history += [E(S('assistant'), result.content[0])]
        return result