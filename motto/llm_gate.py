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
    result = {
        r"atom2msg": msgAtom,
        # FIXME: We add this function here, so we can explicitly evaluate results of LLMs, but
        # we may either expect that this function appear in core MeTTa or need a special safe eval
        r"_eval": OperationAtom("_eval",
                                lambda atom: metta.run("! " + atom.get_object().value)[0],
                                unwrap=False),
        r"contains-str": containsStrAtom,
        r"concat-str": concatStrAtom,
        r"message2tuple": message2tupleAtom

    }
    if importlib.util.find_spec('anthropic') is not None:
        result[r"anthropic-agent"] = AnthropicAgent.agent_creator_atom(metta)
    if importlib.util.find_spec('tiktoken') is not None:
        if (importlib.util.find_spec('bs4') is not None) \
                and (importlib.util.find_spec('markdown') is not None):
            result[r"retrieval-agent"] = RetrievalAgent.agent_creator_atom(metta)
    result[r"chat-gpt-agent"] = ChatGPTAgent.agent_creator_atom(metta)
    result[r"metta-script-agent"] = MettaScriptAgent.agent_creator_atom(metta, unwrap=False)
    result[r"metta-agent"] = MettaAgent.agent_creator_atom(unwrap=False)
    result[r"dialog-agent"] = DialogAgent.agent_creator_atom(unwrap=False)
    result[r"echo-agent"] = EchoAgent.agent_creator_atom(metta)
    result[r"open-router-agent"] = OpenRouterAgent.agent_creator_atom(metta)
    return result

def str_find_all(str, values):
    return list(filter(lambda v: v in str, values))

@register_atoms
def postproc_atoms():
    strfindAtom = OperationAtom('str-find-all', str_find_all)
    return {
        r"str-find-all": strfindAtom,
    }
