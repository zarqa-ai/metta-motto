from hyperon import MeTTa, ValueAtom, E, S
from motto.llm_gate import llm
from motto.agents import EchoAgent, MettaAgent, DialogAgent

def test_stream_response():
    m = MeTTa()
    # we can run metta code from python directly and motto works
    m.run('!(import! &self motto)')
    result = m.run('!(llm (Agent (chat-gpt "gpt-3.5-turbo" True)) (user "Who is John Lennon?"))', True)
    assert hasattr(result[0].get_object().content, "__stream__")

def test_chat_gpt_ext():
    m = MeTTa()
    # we can run metta code from python directly and motto works
    m.run('!(import! &self motto)')
    # set stream = True and cut_history = True
    result = m.run('!(llm (Agent (chat-gpt-ext "gpt-3.5-turbo" True True)) (user "Who is John Lennon?"))', True)
    assert hasattr(result[0].get_object().content, "__stream__")
    # set stream = False and cut_history = True
    result = m.run('!(llm (Agent (chat-gpt-ext "gpt-3.5-turbo" False True)) (user "Say meow"))', True)
    assert "meow" in str(result[0].get_object().content).lower()