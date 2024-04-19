!(import! &self motto)
!(import! &self langchain_examples:langchain_states)
!(set-langchain-model ((py-atom langchain_anthropic.ChatAnthropic) (Kwargs (model "claude-2.1"))))
!(llm (Agent langchain_examples/langchain_agent.msa)(user "What is the name of the airport in Cali, Colombia?"))



