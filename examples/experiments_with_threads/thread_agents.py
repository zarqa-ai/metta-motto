from hyperon import *
from hyperon.exts.agents import AgentObject
from motto.agents import DialogAgent
from queue import Queue
from time import sleep
from motto import get_sentence_from_stream_response
class ListeningAgent(AgentObject):
    def __init__(self, path):
        if path is None and code is None:
            return
        self.messages = Queue()
        self.running = False
        self.daemon = True
        self.cancel_processing_var = False
        if isinstance(path, ExpressionAtom):# and path != E():
            self.dialog_agent = DialogAgent(code=path)
            path = None
        else:
            self.dialog_agent = DialogAgent(path=path)
    def __call__(self, additional_info=None):
        self.running = True
        cnt = 0
        while self.running:
            if not self.messages.empty():
                m = self.messages.get()
                self.output = []
                response = self.dialog_agent(f"(Messages (user \"{m}\"))", additional_info=additional_info).content
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
            self.dialog_agent.history.pop()
            can_close = hasattr(response, "close")
            for i, sentence in enumerate(stream):
                if (i == 0) and self.cancel_processing_var:
                    #self.log.debug("Stream processing has been canceled")
                    if can_close:
                        response.close()
                    break
                self.dialog_agent.history += [E(S("assistant"), G(ValueObject(sentence)))]
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
