import time
from hyperon import *
from motto.agents import DialogAgent, MettaAgent
from hyperon.ext import register_atoms
from hyperon.atoms import GroundedAtom
from queue import Queue
import threading
from motto.utils import *

class AgentArgs:
    def __init__(self, message, functions=[], additional_info=None):
        self.message = message.get_object().content if isinstance(message, GroundedAtom) else message
        self.additional_info = additional_info.get_object().content if isinstance(additional_info, GroundedAtom) else additional_info
        self.functions = functions.get_object().content if isinstance(functions, GroundedAtom) else functions

class Event:
    def __init__(self, event_type, data=None):
        if isinstance(event_type, GroundedAtom):
            event_type = event_type.get_object().content
        if isinstance(data, GroundedAtom):
            data = data.get_object().content
        self.event_type = event_type
        self.data = data
        self.time =  time.time()

class ListeningAgent(DialogAgent):
    # this method will be called via start in separate thread
    def __init__(self, path=None, atoms={}, include_paths=None, code=None):
        self.events = Queue()
        self.cancel_processing_var = False
        self.interrupt_processing_var = False
        super().__init__(path, atoms, include_paths, code)


    def _postproc(self, response):
        # do not need to save history here so the method from MettaAgent is used
        result = MettaAgent._postproc(self, response)
        return result

    def process_stream_response(self, response):
        if response is None:
            return
        if isinstance(response, str):
            if not  self.cancel_processing_var:
                yield response
        else:
            stream = get_sentence_from_stream_response(response)
            can_close = hasattr(response, "close")
            for i, sentence in enumerate(stream):
                if (i == 0) and  (self.cancel_processing_var or self.interrupt_processing_var):
                    self.log.debug("Stream processing has been canceled")
                    if can_close:
                        response.close()
                    break
                yield sentence


    def set_canceling_variable(self, value):
        with self.lock:
            self.cancel_processing_var = value
        return []

    def set_interrupt_variable(self, value):
        with self.lock:
            self.interrupt_processing_var = value
        return []

    def message_processor(self, input: AgentArgs):
        '''
        Takes a single message and provides a response if no canceling event has occurred.
        '''
        print("message_processor start:", input.message)
        message = input.message if str(input.message).startswith("(") and  str(input.message).endswith(")") \
            else f"(Messages (user \"{input.message}\"))"
        response = super().__call__(message, input.functions, input.additional_info).content
        with self.lock:
            self.processing = True
        self.handle_event()
        resp = None
        for resp in self.process_stream_response(response):
            self.handle_event()
            #cancel processing of the current message and return the message to the input
            if self.cancel_processing_var:
                self.input(input.message)
                break
            if self.interrupt_processing_var:
                resp = "..."

            self.history += [E(S(assistant_role), G(ValueObject(resp)))]
            yield resp
            #interrupt processing
            if self.interrupt_processing_var:
                break
        print("message_processor finish:", resp)
        with self.lock:
            self.processing = False


    def __call__(self, msgs_atom=None, functions=[], additional_info=None):
        if msgs_atom is not None:
            super().input(AgentArgs(msgs_atom, functions, additional_info))
        return self.start()

    def input(self, msg):
        if isinstance(msg, GroundedAtom):
            msg = msg.get_object().content
        if isinstance(msg, str):
            msg = {"message": msg}
        super().input(AgentArgs(**msg))
        return []

    def handle_event(self):
        if not self.events.empty():
            with self.lock:
                event = self.events.get()
            if event.event_type == 'speechstart':
                if self.processing:
                    self.set_canceling_variable(not self.said)
                self.speech_start = event.time
            elif event.event_type == 'speechcont' and self.processing and self.said:
                if time.time() - self.speech_start > 0.5:
                    self.set_interrupt_variable(True)
            elif event.event_type == 'speech':
                self.set_canceling_variable(False)
                self.set_interrupt_variable(False)
                self.input(event.data["text"])

    def set_event(self, event_type, data=None):
        '''Adds a new event to the events queue.'''
        with self.lock:
            self.events.put(Event(event_type, data))
        print(event_type)
        return []

    def say(self):
        respond = []
        while not self._output.empty():
            with self.lock:
                self.said = True
                respond.append(self._output.get())
        return [ValueAtom(" ".join(respond))]


    def has_output(self):
        return not self._output.empty()

@register_atoms(pass_metta=True)
def listening_gate_atoms(metta):
    return {
        r"listening-agent": ListeningAgent.agent_creator_atom(unwrap=False),
    }
