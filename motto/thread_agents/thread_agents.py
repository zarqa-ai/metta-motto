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
    def message_processor(self, input:AgentArgs):
        output = []
        response = super().__call__(f"(Messages (user \"{input.message}\"))", input.functions, input.additional_info).content
        for resp in self.process_stream_response(response):
            output.append(resp)
        return output

    def __call__(self, msgs_atom=None, functions=[], additional_info=None):
        return self.start()

    def input(self, msg):
        if isinstance(msg, GroundedAtom):
            msg = msg.get_object().content
            if isinstance(msg, str):
                msg = {"message": msg}
        with self.lock:
            self.cancel_processing_var = False
        super().input(AgentArgs(**msg))
        return []

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
