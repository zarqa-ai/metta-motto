from hyperon import *
from hyperon.exts.agents import AgentObject
import json

import logging
logger = logging.getLogger(__name__)


def to_nested_expr(xs):
    if isinstance(xs, list):
        return E(*list(map(to_nested_expr, xs)))
    if isinstance(xs, dict):
        return E(*[E(to_nested_expr(k), to_nested_expr(v)) for k, v in xs.items()])
    return xs if isinstance(xs, Atom) else ValueAtom(xs)

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

def get_func_def(fn, metta, prompt_space):
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
        # NOTE: metta-type is passed to an LLM as well, which is tolerated atm
        prop = {"type": "string",
                "description": p[1].get_object().value,
                "metta-type": 'String',
               }
        if isinstance(p[0], ExpressionAtom):
            par_typ = p[0].get_children()
            if repr(par_typ[0]) != ':':
                raise TypeError(f"{p[0]} can only be a typing expression")
            par_name = repr(par_typ[1])
            prop["metta-type"] = repr(par_typ[2])
        else:
            par_name = p[0].get_name()
        if len(p) > 2:
            # FIXME? atom2msg or repr or ...?
            prop["enum"] = list(map(lambda x: atom2msg(x), p[2].get_children()))
        properties.update({par_name: prop})
    # FIXME: This function call format is due to ChatGPT. It seems like an excessive
    # wrapper here and might be reduced (and extended in the gpt-agent itself).
    return {
        "name": fn.get_name(),
        "description": doc[1].get_children()[1].get_object().value,
        "parameters": {
            "type": "object",
            "properties": properties
        }
    }

def is_space(atom):
    return isinstance(atom, GroundedAtom) and \
           isinstance(atom.get_object(), SpaceRef)


def get_llm_args(metta: MeTTa, prompt_space: SpaceRef, *args):
    messages = []
    functions = []
    params = {}
    msg_atoms = []
    def __msg_update(m, f, p, a):
        nonlocal messages, functions, params, msg_atoms
        messages += m
        functions += f
        params.update(p)
        msg_atoms += [a]

    for atom in args:
        # We first interpret the atom argument in the context of the main metta space.
        # If the prompt template is in a separate file and contains some external
        # symbols like (user-query), they will be resolved here.
        # It is useful for messages as well as arbitrary code, which relies
        # on information from the agent.
        # TODO: we may want to do something special with equalities
        #arg = interpret(metta.space(), atom)
        arg = metta.evaluate_atom(atom)
        # NOTE: doesn't work now since Error inside other expressions is not passed through them
        #       but it can be needed in the future
        #if isinstance(arg, ExpressionAtom) and repr(arg.get_children()[0]) == 'Error':
        #    raise RuntimeError(repr(arg.get_children()[1]))
        arg = atom if len(arg) == 0 else arg[0]
        if is_space(arg):
            # Spaces as prompt templates should be wrapped into Script argument
            continue
        elif isinstance(arg, ExpressionAtom):
            ch = arg.get_children()
            if len(ch) > 1:
                name = ch[0].get_name()
                if name == 'Messages':
                    __msg_update(*get_llm_args(metta, prompt_space, *ch[1:]))
                elif name in ['system', 'user', 'assistant', 'media']:
                    messages += [{'role': name, 'content': atom2msg(ch[1])}]
                    msg_atoms += [arg]
                elif name in ['Functions', 'Function']:
                    functions += [get_func_def(fn, metta, prompt_space)
                                  for fn in ch[1:]]
                elif name == 'Script':
                    if is_space(ch[1]):
                        # FIXME? This will overwrites the current prompt_space if it is set.
                        # It is convenient to have it here to successfully execute
                        # (agent &prompt (Functions fn)), when fn is defined in &prompt.
                        # But (Function fn) can also be put in &prompt directly.
                        # Depending on what is more convenient, this overriding can be changed.
                        prompt_space = ch[1].get_object()
                    else:
                        # TODO: a better way to load a script?
                        m = MeTTa()
                        # TODO: asserts
                        m.run("!(import! &self motto)")
                        with open(atom2msg(ch[1])) as f:
                            m.run(f.read())
                        prompt_space = m.space()
                    __msg_update(*get_llm_args(metta, prompt_space, *prompt_space.get_atoms()))
                elif name == 'Kwargs':
                    for param in ch[1:]:
                        ps = param.get_children()
                        params[repr(ps[0])] = ps[1]
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
    return messages, functions, params, \
        msg_atoms[0] if len(msg_atoms) == 1 else E(S('Messages'), *msg_atoms)

def get_response(metta, agent, response, functions, msgs_atom):
    if not hasattr(response, "tool_calls"):
        # if response is stream
        return [ValueAtom(response)]
    if response.tool_calls is not None:
        result = []
        for tool_call in response.tool_calls:
            fname = tool_call.function.name
            fs = S(fname)
            args = tool_call.function.arguments if isinstance(tool_call.function.arguments, dict) else json.loads(
                tool_call.function.arguments)
            args = {} if args is None else \
                json.loads(args) if isinstance(args, str) else args
            # Here, we check if the arguments should be parsed to MeTTa
            for func in functions:
                if func["name"] != fname:
                    continue
                for k, v in args.items():
                    if func["parameters"]["properties"][k]['metta-type'] == 'Atom':
                        args[k] = metta.parse_single(v)
            result.append(repr(E(fs, to_nested_expr(list(args.values())), msgs_atom)))
        res = f"({' '.join(result)})" if len(result) > 1 else result[0]
        val = metta.parse_single(res)
        return [val]
    # TODO: better way to determine if wrap into atom
    return response.content if isinstance(response.content, list) else \
        [ValueAtom(response.content)]

class Function:
    def __init__(self, name, arguments, format=""):
        self.name = name
        self.forma = format
        self.arguments = arguments

class ToolCall:
    def __init__(self, id, function, type="function"):
        self.id = id
        self.function = function
        self.type = type

class Response:
    def __init__(self, content, functions=None):
        self.content = content
        self.tool_calls = None
        if functions is not None:
            k = 1
            self.tool_calls = []
            for f in functions:
                self.tool_calls.append(ToolCall(k, f))
                k =+ 1

    def __repr__(self):
        return f"Response(content: {self.content}, tool_calls: {self.tool_calls})"

class Agent(AgentObject):

    def __metta_call__(self, *args):
        try:
            messages, functions, params, msgs_atom = get_llm_args(self._metta, None, *args)
        except Exception as e:
            logger.error(e)
            # return [E(S("Error"), ValueAtom(str(e)))]
            raise e
        if self._unwrap:
            for p in params.keys():
                if not isinstance(params[p], GroundedAtom):
                    raise TypeError(f"GroundedAtom is expected as input to a non-MeTTa agent. Got type({params[p]})={type(params[p])}")
                params[p] = params[p].get_object().value
        try:
            response = self(msgs_atom if not self._unwrap else messages,
                            functions, **params)
        except Exception as e:
            logger.error(e)
            raise e
        return get_response(self._metta, self, response, functions, msgs_atom)


class EchoAgent(Agent):

    def __call__(self, messages, functions=[], user_name=[]):
        msg = list(map(lambda m: m['role'] + ' ' + m['content'], messages))
        if user_name:
            msg.append(f'your name is {user_name}')
        msg = '\n'.join(msg)
        fcall = [] if len(functions) > 0 else None
        # A mock function call processing for testing purposes
        for f in functions:
            vcall = None
            if f['description'] in msg:
                prop = f['parameters']['properties']
                for k in prop:
                    if 'enum' in prop[k]:
                        for v in prop[k]['enum']:
                            if prop[k]['description'] + v in msg:
                                vcall = {k: v}
                fcall.append(Function(f['name'], vcall))
        return Response(msg, fcall)
