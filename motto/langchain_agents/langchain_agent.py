from motto.agents import DialogAgent
from hyperon import ExpressionAtom, OperationAtom, ValueAtom, E, S
from hyperon.ext import register_atoms


# from hyperon.stdlib import get_py_atom
# from hyperon import G, AtomType, OperationObject, ValueObject
# default_model = E(E(OperationAtom("py-atom", get_py_atom, unwrap=False), S("langchain_openai.ChatOpenAI")),
#                   E(S("Kwargs"), E(S("model"), G(ValueObject("gpt-3.5-turbo-0125"))),
#                     E(S("temperature"), G(ValueObject(0)))))


class LangchainAgent(DialogAgent):

    def __init__(self, model, path=None, atoms={}, include_paths=None, code=None):

        self.history = []
        self.model = model
        super().__init__(path, atoms, include_paths, code)
        self._metta.space().add_atom(E(S('='), E(S('langchain-model')),
                                 self.model))


@register_atoms(pass_metta=True)
def langchaingate_atoms(metta):
    return {
        r"langchain-agent": LangchainAgent.agent_creator_atom(unwrap=False),
    }
