from hyperon import *
from hyperon.exts.agents.agent_base import StreamMethod
from motto.agents import DialogAgent
from queue import Queue
from time import sleep
from motto import get_sentence_from_stream_response
class ListeningAgent(DialogAgent):
    def __init__(self, path=None, atoms={}, include_paths=None, code=None):
        super().__init__(path, atoms, include_paths, code)
        self.messages = Queue()
        self.running = False
        self.daemon = True
        self.cancel_processing_var = False


    def __metta_call__(self, *args):
        call = True
        method = super().__metta_call__
        if len(args) > 0:
            if isinstance(args[0], SymbolAtom):
                n = args[0].get_name()
                if n[0] == '.' and hasattr(self, n[1:]):
                    method = getattr(self, n[1:])
                    args = args[1:]
                    call = False
                    if self._unwrap:
                        method = OperationObject(f"{method}", method).execute
        st = StreamMethod(method, args)
        st.start()
        if call and self.is_daemon():
            return [E()]
        return st



    def __call__(self, functions=[], additional_info=None):
        self.running = True
        cnt = 0
        while self.running:
            if not self.messages.empty():
                m = self.messages.get()
                self.output = []
                response = super().__call__(f"(Messages (user \"{m}\"))", functions, additional_info).content
                for resp in self.process_stream_response(response):
                    self.output.append(resp)
                if len(self.output) > 0:
                    print(' '.join(self.output))

    def stop(self):
        self.running = False
    def input(self, msg):
            self.cancel_processing_var = False
            self.messages.put(msg)
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
m = MeTTa()
m.register_atom('agnt', ListeningAgent.agent_creator_atom())
print(m.run('''
  ! (bind! &a1 (agnt "experiments_with_threads/simple_call.msa"))
  ! (&a1)
  ! (println! "Agent is running") 
  ! (&a1 .input "who is the 6 president of France")
  ! ((py-atom time.sleep) 2)
  ! (&a1 .input "who is John Lennon?")
  ! (&a1 .cancel_processing)
  ! ((py-atom time.sleep) 2)
  ! (&a1 .stop)
'''))
