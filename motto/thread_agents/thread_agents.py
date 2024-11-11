from hyperon import *
from motto.agents import DialogAgent
from hyperon.ext import register_atoms


class ListeningAgent(DialogAgent):
    # this method will be calld via start in separate thread
    def message_processor(self, message, functions=[], additional_info=None):
        output = []
        response = super().__call__(f"(Messages (user {message}))", functions, additional_info).content
        for resp in self.process_stream_response(response):
            output.append(resp)
        if len(output) > 0:
            print(' '.join(output))
        return output

    def __call__(self, msgs_atom=None, functions=[], additional_info=None):
        return self.start(functions, additional_info)

    def input(self, msg):
        self.cancel_processing_var = False
        super().input(msg)
        return []


@register_atoms(pass_metta=True)
def listening_gate_atoms(metta):
    return {
        r"listening-agent": ListeningAgent.agent_creator_atom(unwrap=False),
    }


if __name__ == '__main__':
    m = MeTTa()
    print(m.run('''
      ! (import! &self motto)
      ! (bind! &a1 (listening-agent "examples/examples_with_threads/simple_call.msa"))
      ! (&a1)
      ! (println! "Agent is running") 
      ! (&a1 .input "who is the 6 president of France")
      ! ((py-atom time.sleep) 2)
      ! (&a1 .input "who is John Lennon?")
      ! (&a1 .cancel_processing)
      ! ((py-atom time.sleep) 2)
      ! (&a1 .stop)
    '''))
