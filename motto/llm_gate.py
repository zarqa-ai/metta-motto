from hyperon import *
from hyperon.ext import register_atoms
from .agents import *
import json

__default_agent = None

def to_nested_expr(xs):
    if isinstance(xs, list):
        return E(*list(map(to_nested_expr, xs)))
    if isinstance(xs, dict):
        return E(*[E(to_nested_expr(k), to_nested_expr(v)) for k, v in xs.items()])
    return ValueAtom(xs)

def atom2msg(atom):
    if isinstance(atom, ExpressionAtom):
        # Avoid () in Expression representation
        txt = ""
        for ch in atom.get_children():
            txt += atom2msg(ch) + " "
        return txt[:-1] + "\n"
    if isinstance(atom, GroundedAtom):
        if isinstance(atom.get_grounded_type(), ExpressionAtom):
            return repr(atom)
        if isinstance(atom.get_object(), ValueObject):
            # Parse String separately to avoid "" in its repr
            v = atom.get_object().value
            if isinstance(v, str):
                return v.replace("\\n", "\n")
    return repr(atom)

def get_llm_args(metta: MeTTa, prompt_space: SpaceRef, *args):
    agent = None
    print(metta.space().query(E(S('Agent'), V('x'))))
    messages = []
    functions = []
    msg_atoms = []
    def __msg_update(ag, m, f, a):
        nonlocal agent, messages, functions, msg_atoms
        if ag is not None:
            agent = ag
        messages += m
        functions += f
        msg_atoms += [a]
    for arg in args:
        if isinstance(arg, GroundedAtom) and \
           isinstance(arg.get_object(), SpaceRef):
            # FIXME? This will overwrites the current prompt_space if it is set.
            # It is convenient to have it here to successfully execute
            # (llm &prompt (Functions fn)), when fn is defined in &prompt.
            # But (function fn) can also be put in &prompt directly.
            # Depending on what is more convenient, this overriding can be changed.
            prompt_space = arg.get_object()
            __msg_update(*get_llm_args(metta, prompt_space, *prompt_space.get_atoms()))
        elif isinstance(arg, ExpressionAtom):
            ch = arg.get_children()
            if len(ch) > 1:
                name = ch[0].get_name()
                if name == 'Messages':
                    __msg_update(*get_llm_args(metta, prompt_space, *ch[1:]))
                elif name in ['system', 'user', 'assistant']:
                    # We have to interpret the message in the main space context,
                    # if the prompt template is in a separate file and contains
                    # some external symbols like (user-query)
                    msg = interpret(metta.space(), ch[1])[0]
                    messages += [{'role': name, 'content': atom2msg(msg)}]
                    msg_atoms += [arg]
                elif name in ['Functions', 'function']:
                    for fn in ch[1:]:
                        doc = None
                        if prompt_space is not None:
                            # TODO: Querying for a function description in prompt_space works well,
                            # but it is useless, because this function cannot be called
                            # from the main script, so the functional call is not reduced.
                            # Fixing this requires in general better library management in MeTTa,
                            # although it can be managed here by interpreting the functional call expression.
                            # Another approach would be to have load-template, which will import all functions to &self
                            # (or just to declare function in separate files and load to self, since we may want them
                            # to be reusable between templates)
                            r = prompt_space.query(E(S('='), E(S('doc'), fn), V('r')))
                            if not r.is_empty():
                                doc = r[0]['r']
                        if doc is None:
                            # We use `match` here instead of direct `doc` evaluation
                            # to evoid non-reduced `doc`
                            doc = metta.run(f"! (match &self (= (doc {fn}) $r) $r)")
                            if len(doc) == 0 or len(doc[0]) == 0:
                                raise RuntimeError(f"No {fn} function description")
                            doc = doc[0][0]
                        # TODO: format is not checked
                        doc = doc.get_children()
                        properties = {}
                        for par in doc[2].get_children()[1:]:
                            p = par.get_children()
                            properties.update({
                                p[0].get_name(): {
                                    "type": "string",
                                    "description": p[1].get_object().value,
                                    # FIXME? atom2msg or repr or ...?
                                    "enum": list(map(lambda x: atom2msg(x), p[2].get_children()))
                                }
                            })
                        functions += [{
                            "name": fn.get_name(),
                            "description": doc[1].get_children()[1].get_object().value,
                            "parameters": {
                                "type": "object",
                                "properties": properties
                            }
                        }]
                elif name == 'Agent':
                    # We have to interpret it, because if it is (chat-gpt model) in a
                    # script space, it is not yet evaluated
                    agent = interpret(metta.space(), ch[1])[0]
                    # The agent can be a Python object or a string (filename)
                    if isinstance(agent, GroundedAtom):
                        agent = agent.get_object().value
                    elif isinstance(agent, SymbolAtom):
                        agent = agent.get_name()
                    else:
                        raise TypeError(f"Agent {agent} is not identified")
                elif name == '=':
                    # We ignore equalities here: if a space is used to store messages,
                    # it can contain equalities as well (another approach would be to
                    # ignore everythins except valid roles)
                    continue
                else:
                    raise RuntimeError("Unrecognized argument: " + repr(arg))
            else:
                # Ignore an empty expression () for convenience, but we need
                # to put it back into msg_atoms to keep the structure
                msg_atoms += [arg]
        else:
            raise RuntimeError("Unrecognized argument: " + repr(arg))
    # Do not wrap a single message into Message (necessary to avoid double
    # wrapping of single Message argument)
    return agent, messages, functions, \
        msg_atoms[0] if len(msg_atoms) == 1 else E(S('Messages'), *msg_atoms)


def llm(metta: MeTTa, *args):
    agent, messages, functions, msgs_atom = get_llm_args(metta, None, *args)
    if agent is None:
        agent = __default_agent
    if isinstance(agent, str):
        agent = MettaAgent(metta, agent)
    if not isinstance(agent, Agent):
        raise TypeError(f"Agent {agent} should be of Agent type. Got {type(agent)}")
    response = agent(msgs_atom if isinstance(agent, MettaAgent) else messages,
                     functions)
    if response.function_call is not None:
        fs = S(response.function_call.name)
        args = response.function_call.arguments
        args = {} if args is None else \
            json.loads(args) if isinstance(args, str) else args
        return [E(fs, to_nested_expr(list(args.values())), msgs_atom)]
    return [ValueAtom(response.content)]


@register_atoms(pass_metta=True)
def llmgate_atoms(metta):
    global __default_agent
    __default_agent = ChatGPTAgent()
    llmAtom = OperationAtom('llm', lambda *args: llm(metta, *args), unwrap=False)
    # Just a helper function if one needs to print from a metta-script
    # the message converted from expression to text
    msgAtom = OperationAtom('atom2msg',
                 lambda atom: [ValueAtom(atom2msg(atom))], unwrap=False)
    chatGPTAtom = OperationAtom('chat-gpt',
                     lambda model: ChatGPTAgent(model))
    echoAgentAtom = ValueAtom(EchoAgent())
    return {
        r"llm": llmAtom,
        r"atom2msg": msgAtom,
        r"chat-gpt": chatGPTAtom,
        r"EchoAgent": echoAgentAtom,
    }


def str_find_all(str, values):
    return list(filter(lambda v: v in str, values))

@register_atoms
def postproc_atoms():
    strfindAtom = OperationAtom('str-find-all', str_find_all)
    return {
        r"str-find-all": strfindAtom,
    }
