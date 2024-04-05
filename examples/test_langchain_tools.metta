!(import! &self motto)
(llm
    (Agent (chat-gpt))
    (user "What is the weather in Moscow?")
    (langchain_tool tavily_answer))

(llm
    (Agent (chat-gpt))
    (user "What is the weather in Moscow?")
    (langchain_tool google_search))

;!(bind! &openai-tools (Agent (openai-tools-agent  "tavily_answer;google_search" )))
;!(bind! &openai-tools (Agent (openai-tools-agent  "tavily_answer")))
;!(llm &openai-tools   (user "What is the weather in Moscow?"))

!(bind! &openai-tools (Agent (openai-tools-agent  "amadeus_toolkit")))
!(llm &openai-tools   (user "What is the name of the airport in Cali, Colombia?"))