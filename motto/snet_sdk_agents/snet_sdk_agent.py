from motto import get_string_value

from motto.agents import MettaAgent
from hyperon import ExpressionAtom, OperationAtom, ValueAtom, E, S, V, MeTTa, Environment, GroundingSpaceRef, G
from hyperon.ext import register_atoms
from hyperon.exts import snet_io
from motto.agents import Response


class SnetSDKAgent(MettaAgent):

    def __init__(self, org_id, service_id, method_args, kwargs=None, include_paths=None):
        self.history = []
        self.org_id = org_id #get_string_value(org_id)
        self.service_id = service_id #get_string_value(service_id)
        self._include_paths = include_paths
        self._atoms = {}
        super()._init_metta()
        self._context_space = None
        self.method_args = method_args #method_args.get_object().value
        # create create_service_client and space with methods generated for given service
        wrapper = snet_io.SNetSDKWrapper()
        wrapper.init_sdk()
        sp = wrapper.create_service_space(self.org_id, self.service_id, **kwargs) if kwargs is not None else wrapper.create_service_space(self.org_id, self.service_id)
        self.service_space = sp[0]
        self._metta.space().add_atom(self.service_space)

    def _prepare(self, msgs_atom, additional_info=None):
        super()._prepare(None)
        message = ""
        #add user message to "(query)"
        for msg in msgs_atom:
            if 'content' in msg:
                message += msg['content'] + " "
        context_space = self._context_space.get_object()
        context_space.add_atom(E(S('='), E(S('query')), ValueAtom(message)))

    def __call__(self, msgs_atom, functions=[], additional_info=None):
        # TODO: support {'role': , 'content': } dict input
        if isinstance(msgs_atom, str):
            msgs_atom = self._metta.parse_single(msgs_atom)
        self._prepare(msgs_atom)
        args = []
        for k, v in self.method_args.items():
            args.append(S(get_string_value(v)))
        # call the method of service with initialised (query)
        response = self._metta.run(f'!{E(*args)}')
        return self._postproc(response[0])

    def _postproc(self, response):
        # No postprocessing is needed here
        return Response(response, None)


@register_atoms(pass_metta=True)
def snet_sdk_atoms(metta):
    return {
        r"snet-sdk-agent": SnetSDKAgent.agent_creator_atom(),
    }
