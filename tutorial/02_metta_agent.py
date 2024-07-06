from motto.agents import MettaScriptAgent

# There is MettaScriptAgent, which can be used from Python.
# It should execute Response as its output.
# It can do anything (e.g. implement a rule-based system with intent recognition, etc.)
# `(messages)` is used by MettaScriptAgent to get the input messages.
agent = MettaScriptAgent(code='''
    (= (respond (user Ping)) "Pong")
    ! (Response (respond (messages)))
''')
print(agent('(user Ping)').content)

# But it can also call another agent including ChatGPT via llm,
# which can include a function call, which will be evaluated in
# the MeTTa agent right away.
agent = MettaScriptAgent(path='02_metta_agent.msa')

print(agent('(user "Calculate 109 times 11")').content)
