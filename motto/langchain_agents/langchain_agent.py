from motto.agents import DialogAgent
from hyperon import ExpressionAtom, OperationAtom, ValueAtom, E, S
from hyperon.ext import register_atoms


class LangchainAgent(DialogAgent):

    def __init__(self, model, path=None, code=None, atoms={}, include_paths=None):
        self.history = []
        self.model = model
        super().__init__(path, code, atoms, include_paths)

    def _prepare(self, metta, msgs_atom):
        super()._prepare(metta, msgs_atom)

        metta.space().add_atom(E(S('='), E(S('history')),
                                 E(*self.history)))
        metta.space().add_atom(E(S('='), E(S('langchain-model')),
                                 self.model))
        # atm, we put the input message into the history by default

        self.history += [msgs_atom]


@register_atoms(pass_metta=True)
def langchaingate_atoms(metta):
    langchainAtom = OperationAtom('langchain-agent',
                                  lambda m, x: [
                                      ValueAtom(LangchainAgent(model=m, code=x) if isinstance(x, ExpressionAtom) else \
                                                    LangchainAgent(model=m, path=x))],
                                  type_names=['Atom', '%Undefined%', 'Atom'], unwrap=False)
    return {
        r"langchain-agent": langchainAtom,

    }
