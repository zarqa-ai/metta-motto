from hyperon import MeTTa, ValueAtom, E, S
from motto.llm_gate import llm
from motto.agents import MettaAgent

def test_python_metta_direct():
    m = MeTTa()
    # we can run metta code from python directly and motto works
    m.run('!(extend-py! motto)')
    assert m.run('!(llm (Agent basic_agent.msa) (user "Ping"))') == \
        [[ValueAtom("assistant Pong")]]

def test_python_metta_agent():
    m = MeTTa()
    # we can run metta agent directly (also from code string)
    a = MettaAgent(m, code = '''
    (= (proc-messages (user "Ping")) (assistant "Pong"))
    !(Response (llm (Agent EchoAgent) (proc-messages (messages))))
    ''')
    msgs_atom = m.parse_single('(user "Ping")')
    assert a(msgs_atom, None).content == "assistant Pong"
    # we can also call llm directly, but the main purpose of llm is to unwrap atoms
    # for the agent call, so it usually makes more sense to call the agent directly
    # but we do this here for the testing purpose
    assert llm(m, msgs_atom, E(S('Agent'), ValueAtom(a))) == \
        [ValueAtom("assistant Pong")]
