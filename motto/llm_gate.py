from hyperon import *
from hyperon.ext import register_atoms
from .agents import *
from .utils import *
import importlib.util

@register_atoms(pass_metta=True)
def llmgate_atoms(metta):
    # Just a helper function if one needs to print from a metta-script
    # the message converted from expression to text
    msgAtom = OperationAtom('atom2msg',
                    lambda atom: [ValueAtom(atom2msg(atom))], unwrap=False)
    containsStrAtom = OperationAtom('contains-str', lambda a, b: [ValueAtom(contains_str(a, b))], unwrap=False)
    concatStrAtom = OperationAtom('concat-str', lambda a, b: [ValueAtom(concat_str(a, b))], unwrap=False)
    message2tupleAtom = OperationAtom('message2tuple', lambda a: [ValueAtom(message2tuple(a))], unwrap=False)
    result = {r"atom2msg": msgAtom, r"_eval": OperationAtom("_eval",
                                                            lambda atom: metta.run("! " + atom.get_object().value)[0],
                                                            unwrap=False), r"contains-str": containsStrAtom,
              r"concat-str": concatStrAtom, r"message2tuple": message2tupleAtom,
              r"anthropic-agent": AnthropicAgent.agent_creator_atom(metta),
              r"retrieval-agent": RetrievalAgent.agent_creator_atom(metta),
              r"chat-gpt-agent": ChatGPTAgent.agent_creator_atom(metta),
              r"metta-script-agent": MettaScriptAgent.agent_creator_atom(metta, unwrap=False),
              r"metta-agent": MettaAgent.agent_creator_atom(unwrap=False),
              r"dialog-agent": DialogAgent.agent_creator_atom(unwrap=False),
              r"echo-agent": EchoAgent.agent_creator_atom(metta),
              r"open-router-agent": OpenRouterAgent.agent_creator_atom(metta)}

    return result

def str_find_all(str, values):
    return list(filter(lambda v: v in str, values))

@register_atoms
def postproc_atoms():
    strfindAtom = OperationAtom('str-find-all', str_find_all)
    return {
        r"str-find-all": strfindAtom,
    }
