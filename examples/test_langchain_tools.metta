!(import! &self motto)
!(llm
    (Agent (chat-gpt))
    (user "What is the weather in Moscow?")
    (langchain_tool tavily_answer))

!(llm
    (Agent (chat-gpt))
    (user "What is the weather in Moscow?")
    (langchain_tool google_search))