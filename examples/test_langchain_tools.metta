!(import! &self motto)
;use of openai-tools-agent
!(import-from langchain_community.tools.google_search import GoogleSearchRun)
!(import-from langchain_community.utilities import GoogleSearchAPIWrapper)
!(bind! runner (run-py (GoogleSearchRun (api_wrapper GoogleSearchAPIWrapper))))
!(bind! &openai-tools (Agent (openai-tools-agent  runner)))
!(llm &openai-tools   (user "What is the weather in Moscow?"))

;use of openai-tools-agent for toolkit
;!(import-from langchain_community.tools.tavily_search import TavilySearchResults)
;!(bind! runner (run-py TavilySearchResults))
;!(bind! &openai-tools (Agent (openai-tools-agent  runner)))
;!(llm &openai-tools   (user "What is the name of the airport in Cali, Colombia?"))

;use arxiv tool
;!(import-from langchain_community.tools.arxiv.tool import ArxivQueryRun)
;!(bind! runner (run-py ArxivQueryRun))
;!(bind! &openai-tools (Agent (openai-tools-agent  runner)))
;!(llm &openai-tools   (user "What's the paper 1605.08386 about?"))


