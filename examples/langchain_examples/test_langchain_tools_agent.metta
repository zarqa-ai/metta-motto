!(import! &self motto)
!(import! &self langchain_examples:langchain_states)

!(bind! &google_tool ((py-atom langchain_community.tools.google_search.GoogleSearchRun)
    (Kwargs (api_wrapper ((py-atom   langchain_community.utilities.GoogleSearchAPIWrapper))))))

!(bind! &tavily_tool ((py-atom langchain_community.tools.tavily_search.TavilySearchResults)))
!(bind! &arxiv_tool ((py-atom langchain_community.tools.arxiv.tool.ArxivQueryRun)))

!(set-langchain-tools  (py-list &google_tool &tavily_tool &arxiv_tool))

!(llm (Agent langchain_examples/langchain_openai_tools_agent.msa)(user  "What is the name of the airport in Cali, Colombia?"))
!(llm (Agent langchain_examples/langchain_openai_tools_agent.msa)(user "What's the paper 1605.08386 about?"))
!(llm (Agent langchain_examples/langchain_openai_tools_agent.msa)(user "What is the weather in Moscow?"))



