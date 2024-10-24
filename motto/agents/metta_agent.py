import logging

from .agent import Agent, Response
from hyperon import *
from motto.utils import *

assistant_role = 'assistant'


class MettaAgent(Agent):

    def _init_metta(self):
        super()._init_metta()
        # TODO: assert
        self._metta.run("!(import! &self motto)")

    def _prepare(self, msgs_atom, additional_info=None):
        # The context space is recreated on each call
        if self._context_space is not None:
            self._metta.space().remove_atom(self._context_space)
        self._context_space = G(GroundingSpaceRef())
        self._metta.space().add_atom(self._context_space)
        context_space = self._context_space.get_object()
        if msgs_atom is not None:
            context_space.add_atom(E(S('='), E(S('messages')), msgs_atom))
        # what to do if need to set some variables from python?
        if additional_info is not None:
            for val in additional_info:
                f, v, t = val
                context_space.add_atom(
                    E(S(':'), S(f), E(S('->'), S(t))))
                context_space.add_atom(
                    E(S('='), E(S(f)), ValueAtom(v)))

    def _postproc(self, response):
        # No postprocessing is needed here
        return Response(response, None)

    def __call__(self, msgs_atom, functions=[], additional_info=None):
        # TODO: support {'role': , 'content': } dict input
        if isinstance(msgs_atom, str):
            msgs_atom = self._metta.parse_single(msgs_atom)
        self._prepare(msgs_atom, additional_info)
        response = self._metta.run('!(response)')
        return self._postproc(response[0])


class MettaScriptAgent(MettaAgent):

    def _create_metta(self):
        # Skipping _create_metta in super.__init__
        pass

    def __call__(self, msgs_atom, functions=[], additional_info=None):
        self._init_metta()
        if isinstance(msgs_atom, str):
            msgs_atom = self._metta.parse_single(msgs_atom)
        self._prepare(msgs_atom, additional_info)
        # Loading the code after _prepare
        super()._load_code()
        response = self._metta.run('!(response)')
        return self._postproc(response[0])


class DialogAgent(MettaAgent):

    def __init__(self, path=None, atoms={}, include_paths=None, code=None):
        self.history = []
        super().__init__(path, atoms, include_paths, code)
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.perform_canceling = False

    def _prepare(self, msgs_atom, additional_info=None):
        super()._prepare(msgs_atom, additional_info)
        self._context_space.get_object().add_atom(
            E(S('='), E(S('history')), E(S('Messages'), *self.history)))
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
        self.history += [E(S(assistant_role), result.content[0])]
        return result

    def clear_history(self):
        self.history = []

    def get_response_by_index(self, index, role=assistant_role):
        last_response = self.history[index]
        if hasattr(last_response, "get_children"):
            children = last_response.get_children()
            if len(children) == 2 and (children[0].get_name() == role):
                response = children[1].get_object().content
                return response
        return None

    def process_last_stream_response(self):
        response = self.get_response_by_index(-1)
        if response is None:
            return
        if isinstance(response, str):
            if not self.perform_canceling:
                yield response
        else:
            stream = get_sentence_from_stream_response(response)
            self.history.pop()
            can_close = hasattr(response, "close")
            for i, sentence in enumerate(stream):
                if (i == 0) and self.perform_canceling:
                    self.log.debug("Stream processing has been canceled")
                    if can_close:
                        response.close()
                    break
                self.history += [E(S(assistant_role), G(ValueObject(sentence)))]
                yield sentence
