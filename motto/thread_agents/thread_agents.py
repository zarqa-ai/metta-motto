import time

from hyperon import *
from motto.agents import DialogAgent
from hyperon.ext import register_atoms

class AgentArgs:
    def __init__(self, message, functions=[], additional_info=None):
        self.message = message
        self.additional_info = additional_info
        self.functions = functions


class ListeningAgent(DialogAgent):
    # this method will be called via start in separate thread
    def __init__(self, path=None, atoms={}, include_paths=None, code=None):
        self.speech_start = None
        self.processing =  True
        super().__init__(path, atoms, include_paths, code)

    def message_processor(self, input: AgentArgs):
        output = []
        response = super().__call__(f"(Messages (user \"{input.message}\"))", input.functions, input.additional_info).content
        self.processing = True
        for resp in self.process_stream_response(response):
            output.append(resp)
        self.processing = False
        return output

    def __call__(self, msgs_atom=None, functions=[], additional_info=None):
        return self.start()

    def input(self, msg):
        if isinstance(msg, GroundedAtom):
            msg = msg.get_object().content
            if isinstance(msg, str):
                msg = {"message": msg}
        super().input(AgentArgs(**msg))
        return []

    def handle_event(self, event_type, data):
        if event_type == 'speechstart':
            self.speech_start = time.time()
            with self.lock:
                self.cancel_processing_var = self.processing
        elif event_type == 'speechcont' and self.processing:
            if time.time() - self.speech_start < 0.5:
                with self.lock:
                    self.interrupt_processing = True
            with self.lock:
                self.cancel_processing_var = True
        elif event_type == 'speech':
            self.input(data["text"])
            with self.lock:
                self.cancel_processing_var = self.processing


    def get_output(self):
        if len(self._output) == 0:
            return []
        return [ValueAtom(" ".join(self._output))]

    def clear_output(self):
        with self.lock:
            self._output.clear()


@register_atoms(pass_metta=True)
def listening_gate_atoms(metta):
    return {
        r"listening-agent": ListeningAgent.agent_creator_atom(unwrap=False),
    }
