from .agent import Agent, Response
from hyperon import *

class MettaScriptAgent(Agent):

    def _try_unwrap(self, val):
        if val is None or isinstance(val, str):
            return val
        if isinstance(val, GroundedAtom):
            return str(val.get_object().content)
        return repr(val)

    def __init__(self, path=None, code=None, atoms={}, include_paths=None):
        if isinstance(path, ExpressionAtom): # A hack to pass code here from MeTTa
            code = path
            path = None
        self._path = self._try_unwrap(path)
        self._code = code.get_children()[1] if isinstance(code, ExpressionAtom) else \
                     self._try_unwrap(code)
        if path is None and code is None:
            raise RuntimeError(f"{self.__class__.__name__} requires either path or code")
        self._atoms = atoms
        self._includes = include_paths

    def _prepare(self, metta, msgs_atom, additional_info=None):
        for k, v in self._atoms.items():
            metta.register_atom(k, v)
        metta.space().add_atom(E(S('='), E(S('messages')), msgs_atom))
        # what to do if need to set some variables from python?
        if (additional_info is not None) :
            for val in additional_info:
                f, v, t = val
                x = metta.parse_single(f"(: {f} (-> '{t}'))")
                metta.space().add_atom(x)
                metta.space().add_atom(E(S('='), E(S(f)), ValueAtom(v)))

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

    def __call__(self, msgs_atom, functions=[], additional_info=None):
        # FIXME: we cannot use higher-level metta here (e.g. passed by llm func),
        # from which an agent can be called, because its space will be polluted.
        # Thus, we create new metta runner and import motto.
        # We could avoid importing motto each time by reusing tokenizer or by
        # swapping its space with a temporary space, but current API is not enough.
        # It could also be possible to import! the agent script into a new space,
        # but there is no function to do this without creating a new token
        # (which might be useful). The latter solution will work differently.
        if self._includes is not None:
            env_builder = Environment.custom_env(include_paths=self._includes)
            metta = MeTTa(env_builder=env_builder)
        else:
            metta = MeTTa()
        # TODO: assert
        metta.run("!(import! &self motto)")
        #metta.load_module_at_path("motto")
        # TODO: support {'role': , 'content': } dict input
        if isinstance(msgs_atom, str):
            msgs_atom = metta.parse_single(msgs_atom)
        self._prepare(metta, msgs_atom, additional_info)
        if self._path is not None:
            #response = metta.load_module_at_path(self._path)
            with open(self._path, mode='r') as f:
                code = f.read()
                response = metta.run(code)
        if self._code is not None:
            response = metta.run(self._code) if isinstance(self._code, str) else \
                       [metta.evaluate_atom(self._code)]
                       #[interpret(metta.space(), self._code)]
        return self._postproc(response)


class DialogAgent(MettaScriptAgent):

    def __init__(self, path=None, code=None, atoms={}, include_paths=None):
        self.history = []
        super().__init__(path, code, atoms, include_paths)

    def _prepare(self, metta, msgs_atom,  additional_info=None):
        super()._prepare(metta, msgs_atom, additional_info)
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

    def clear_history(self):
        self.history = []

class MettaBaseAgent(Agent):
    pass
