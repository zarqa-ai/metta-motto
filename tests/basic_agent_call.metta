!(import! &self motto)

(= (no-new-expression) True)

!(assertEqual
  ((metta-script-agent "basic_agent.msa") (user "Ping"))
  "assistant Pong")

!(assertEqual
  ((metta-script-agent "basic_agent.msa") (system "Ping"))
  "assistant gniP")

!(assertEqual (no-new-expression) True)

!(assertEqual
  ((metta-script-agent "basic_agentsc.msa") (user "Hello world."))
"user Hello world.
assistant Hi there")
