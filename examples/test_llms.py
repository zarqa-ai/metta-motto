from hyperon import MeTTa, ValueAtom, E, S
from motto.llm_gate import llm
from motto.agents import EchoAgent, MettaScriptAgent, DialogAgent

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

def test_chat_gpt_ext_additional_info():
    agent = MettaScriptAgent(path="basic_stream_call.msa")
    v = agent('(Messages (system  "You are Grace, you are in London")(user "Say meow"))',
              additional_info=[("model_name", "gpt-3.5-turbo", 'String'), ("is_stream", False, 'Bool')]).content
    result = v[0].get_object().content
    assert "meow" in result.lower()