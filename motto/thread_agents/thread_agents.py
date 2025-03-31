import time
from motto.agents import DialogAgent, MettaAgent
from hyperon.ext import register_atoms
from hyperon.exts.agents.agent_base import StreamMethod
from queue import Queue
import threading
from motto.utils import *
import logging


class AgentArgs:
    def __init__(self, message, functions=[], additional_info=None, language=None):
        self.message = get_grounded_atom_value(message)
        self.additional_info = get_grounded_atom_value(additional_info)
        self.functions = get_grounded_atom_value(functions)
        self.language = language


class ListeningAgent(DialogAgent):
    stop_message = "_stop_"

    # this method will be called via start in separate thread
    def __init__(self, path=None, atoms={}, include_paths=None, code=None, event_bus=None):
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.cancel_processing_var = False
        self.interrupt_processing_var = False
        self.processing = False

        atoms['handle-speechstart'] = OperationAtom('queue-subscription', self.handle_speechstart, unwrap=False)
        atoms['handle-speechcont'] = OperationAtom('handle-speechcont', self.handle_speechcont, unwrap=False)
        atoms['process_messages'] = OperationAtom('process_messages', self.process_messages, unwrap=False)

        if isinstance(atoms, GroundedAtom):
            atoms = atoms.get_object().content
        super().__init__(path, atoms, include_paths, code, event_bus=event_bus)
        self.lock = threading.RLock()
        self.messages = Queue()

    def _postproc(self, response):
        # do not need to save history here so the method from MettaAgent is used
        result = MettaAgent._postproc(self, response)
        return result


    def process_stream_response(self, response):
        if response is None:
            return
        if isinstance(response, str):
            if not self.cancel_processing_var:
                yield response
        else:
            stream = get_sentence_from_stream_response(response)
            can_close = hasattr(response, "close")
            for i, sentence in enumerate(stream):
                if (i == 0) and (self.cancel_processing_var or self.interrupt_processing_var):
                    self.log.debug("Stream processing has been canceled")
                    if can_close:
                        response.close()
                    break
                yield sentence

    def set_canceling_variable(self, value):
        with self.lock:
            self.cancel_processing_var = value

    def set_interrupt_variable(self, value):
        with self.lock:
            self.interrupt_processing_var = value

    def set_processing_val(self, val):
        with self.lock:
            self.processing = val

    def is_empty_message(self, message):
        if isinstance(message, ExpressionAtom):
            children = message.get_children()
            if len(children) > 1 and str(get_grounded_atom_value(children[-1])).strip() == "":
                return True
        elif isinstance(message, str) and message.strip() == "":
            return True
        if message is None:
            return True

        return False

    def process_messages(self, arg):
        input = self.getAgentArgs(arg)
        for resp in self.process_message(input):
            self.outputs.put(resp)
        return []

    def process_message(self, input):
        '''
        Takes a single message and provides a response if no canceling event has occurred.
        '''

        self.said = False
        self.set_canceling_variable(False)
        self.set_interrupt_variable(False)
        if self.is_empty_message(input.message):
            message = None
        elif str(input.message).startswith("(") and str(input.message).endswith(")"):
            message = input.message
        else:
            message = f"(Messages (user \"{input.message}\"))"
        if (message is None) and (input.additional_info is None):
            self.set_processing_val(False)
            return

        self.set_processing_val(True)
        response = super().__call__(message, input.functions, input.additional_info).content
        for resp in self.process_stream_response(response):
            # cancel processing of the current message and return the message to the input
            if self.cancel_processing_var:
                print(f"message_processor:cancel processing for message {message}\n")
                self.event_bus.publish("speech", arg)
                break

            if self.interrupt_processing_var:
                print(f"message_processor:interrupt processing for message {message}\n")
                resp = "..."

            self.history += [E(S(assistant_role), G(ValueObject(resp)))]
            self.log.info(f"message_processor: return response for message {message} : {resp}")
            yield resp if input.language is None else (resp, input.language)
            # interrupt processing
            if self.interrupt_processing_var:
                break
        self.set_processing_val(False)


    def __call__(self, msgs_atom=None, functions=[], additional_info=None):
        return self.start()

    def getAgentArgs(self, msg) -> AgentArgs:
        msg = get_grounded_atom_value(msg)
        if 'text' in msg:
            msg = msg['text']
        if isinstance(msg, str):
            msg = {"message": msg}
        return AgentArgs(**msg)

    def handle_speechstart(self, arg):
        self.speech_start = get_grounded_atom_value(arg)
        if self.processing:
            self.set_canceling_variable(not self.said)
        return []

    def handle_speechcont(self, arg):
        if self.processing and self.said and ((time.time() - self.speech_start) > 0.5):
            self.set_interrupt_variable(True)
        return []



    def stop(self):
        super().stop()
        self.messages.put(AgentArgs(message=self.stop_message))

    def say(self):
        respond = []
        while not self.outputs.empty():
            with self.lock:
                self.said = True
                respond.append(ValueAtom(self.outputs.get()))
        return respond

    def has_output(self):
        return not self.outputs.empty()


@register_atoms(pass_metta=True)
def listening_gate_atoms(metta):
    return {
        r"listening-agent": OperationAtom('listening-agent',
                                          lambda path=None, event_bus=None:
                                          ListeningAgent.get_agent_atom(None,
                                                                      unwrap=False,
                                                                      path=path,
                                                                      event_bus=event_bus),
                                          unwrap=False),
    }
