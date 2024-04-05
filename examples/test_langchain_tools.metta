!(import! &self motto)
(llm
    (Agent (chat-gpt))
    (user "What is the weather in Moscow?")
    (langchain_tool tavily_answer))

(llm
    (Agent (chat-gpt))
    (user "What is the weather in Moscow?")
    (langchain_tool google_search))

;use of openai-tools-agent
; example of several tools definition
;!(bind! &openai-tools (Agent (openai-tools-agent  "tavily_answer;google_search" )))
;!(bind! &openai-tools (Agent (openai-tools-agent  "tavily_answer")))
;!(llm &openai-tools   (user "What is the weather in Moscow?"))

;use of openai-tools-agent for toolkit
;!(bind! &openai-tools (Agent (openai-tools-agent  "amadeus_toolkit")))
;!(llm &openai-tools   (user "What is the name of the airport in Cali, Colombia?"))
;
;use arxiv tool
!(bind! &openai-tools (Agent (openai-tools-agent  "arxiv")))
!(llm &openai-tools   (user "What's the paper 1605.08386 about?"))


!(llm
    (Agent (chat-gpt))
    (user "What's the paper 1605.08386 about?")
    (langchain_tool arxiv))