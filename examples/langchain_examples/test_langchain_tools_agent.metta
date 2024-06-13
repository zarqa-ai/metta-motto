!(import! &self motto)
!(import! &self motto:langchain_agents:langchain_states)
!(bind! &lst (py-list ()))

!((py-dot &lst append) ((py-atom langchain_google_community.GoogleSearchRun)
    (Kwargs (api_wrapper ((py-atom   langchain_google_community.GoogleSearchAPIWrapper))))))

;!((py-dot &lst append)((py-atom langchain_community.tools.tavily_search.TavilySearchResults)))
;!((py-dot &lst append) ((py-atom langchain_community.tools.arxiv.tool.ArxivQueryRun)))

!(set-langchain-agent-executor  &lst)

!(llm (Agent motto/langchain_agents/langchain_openai_tools_agent.msa)(user  "What is the name of the airport in Cali, Colombia?"))
;!(llm (Agent motto/langchain_agents/langchain_openai_tools_agent.msa)(user "What's the paper 1605.08386 about?"))
;!(llm (Agent motto/langchain_agents/langchain_openai_tools_agent.msa)(user "What is the weather in Moscow?"))



