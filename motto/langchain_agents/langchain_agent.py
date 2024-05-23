from motto.agents import DialogAgent
from hyperon import ExpressionAtom, OperationAtom, ValueAtom, E, S
from hyperon.ext import register_atoms

# from hyperon.stdlib import get_py_atom
# from hyperon import G, AtomType, OperationObject, ValueObject
# default_model = E(E(OperationAtom("py-atom", get_py_atom, unwrap=False), S("langchain_openai.ChatOpenAI")),
#                   E(S("Kwargs"), E(S("model"), G(ValueObject("gpt-3.5-turbo-0125"))),
#                     E(S("temperature"), G(ValueObject(0)))))


class LangchainAgent(DialogAgent):

    def __init__(self, model, path=None, code=None, atoms={}, include_paths=None):
        self.history = []
        self.model = model
        super().__init__(path, code, atoms, include_paths)

    def _prepare(self, metta, msgs_atom):
        super()._prepare(metta, msgs_atom)
        metta.space().add_atom(E(S('='), E(S('langchain-model')),
                                 self.model))


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
