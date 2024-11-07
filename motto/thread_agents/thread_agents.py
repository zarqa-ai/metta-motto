from hyperon import *
from motto.agents import DialogAgent
from motto import get_sentence_from_stream_response
from hyperon.ext import register_atoms

class ListeningAgent(DialogAgent):
    def __init__(self, path=None, atoms={}, include_paths=None, code=None):
        super().__init__(path, atoms, include_paths, code)
        self.cancel_processing_var = False

    def __metta_call__(self, *args):
        if len(args) > 0:
            if isinstance(args[0], SymbolAtom):
                n = args[0].get_name()
                if n[0] == '.' and hasattr(self, n[1:]):
                    method = getattr(self, n[1:])
                    args = args[1:]
                    if self._unwrap:
                        method = OperationObject(f"{method}", method).execute
                    return method(*args)
        return super().__metta_call__(*args)

    # this method will be calld via start in separate thread
    def message_processor(self, message,  functions=[], additional_info=None):
        output = []
        response = super().__call__(f"(Messages (user \"{message}\"))", functions, additional_info).content
        for resp in self.process_stream_response(response):
            output.append(resp)
        if len(output) > 0:
            print(' '.join(output))
        return output

    def __call__(self, msgs_atom, functions=[], additional_info=None):
        return self.start(functions, additional_info)

    def input(self, msg):
        self.cancel_processing_var = False
        super().input(msg)

    def cancel_processing(self):
        self.cancel_processing_var = True


    def process_stream_response(self, response):
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
                if (i == 0) and self.cancel_processing_var:
                    #self.log.debug("Stream processing has been canceled")
                    if can_close:
                        response.close()
                    break
                self.history += [E(S("assistant"), G(ValueObject(sentence)))]
                yield sentence

@register_atoms(pass_metta=True)
def listening_gate_atoms(metta):
    return {
        r"listening-agent": ListeningAgent.agent_creator_atom(),
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
