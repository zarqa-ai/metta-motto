from hyperon import MeTTa, ValueAtom
from motto.agents import Agent, Response

class CustomSplitAgent(Agent):
    def __init__(self, word=None):
        super().__init__()
        self.word = word

    def __call__(self, msgs, functions):
        if self.word is None:
            return Response("I need a word to search")
        if self.word in msgs[0]['content']:
            return Response(msgs[0]['content'].split(self.word)[-1])
        return Response("Fail")


def test_custom_agent():
    m = MeTTa()
    m.register_atom('split-agent', CustomSplitAgent.agent_creator_atom(m))
    m.run("!(import! &self motto)")
    assert m.run('''
        !((split-agent) (user "Hello"))
        !((split-agent "name is ") (user "My name is Name"))
        !((split-agent "abracadabra") (user "My name is Name"))
    ''') == [
        [ValueAtom("I need a word to search")],
        [ValueAtom("Name")],
        [ValueAtom("Fail")]]
