from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_core.tools import BaseTool


class LangchainTools:
    @staticmethod
    def get_tool_by_name(tool_name: str) -> BaseTool | None:
        if tool_name == "google_search":
            from langchain_community.tools.google_search import GoogleSearchRun
            from langchain_community.utilities import GoogleSearchAPIWrapper
            return GoogleSearchRun(api_wrapper=GoogleSearchAPIWrapper())
        elif tool_name == "tavily_answer":
            from langchain_community.tools.tavily_search import TavilyAnswer
            from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
            return TavilyAnswer(api_wrapper=TavilySearchAPIWrapper())
        elif tool_name == "arxiv":
            return ArxivQueryRun()
        else:
            return None

    @staticmethod
    def get_function_by_tool_name(tool_name: str):
        tool = LangchainTools.get_tool_by_name(tool_name)
        if tool is not None:
            from langchain.chains.openai_functions import convert_to_openai_function
            return convert_to_openai_function(tool)
        return {}

    @staticmethod
    def get_toolkit_by_name(toolkit_name: str):
        if toolkit_name == "amadeus_toolkit":
            from langchain_community.agent_toolkits.amadeus.toolkit import AmadeusToolkit
            toolkit = AmadeusToolkit()
            return toolkit.get_tools()
        else:
            return None

    @staticmethod
    def collect_tools_and_toolkits_by_name(tools_names):
        tools = []
        for tool in tools_names:
            t = LangchainTools.get_tool_by_name(tool)
            if t is None:
                t = LangchainTools.get_toolkit_by_name(tool)
                if t is not None:
                    tools.extend(t)
            else:
                tools.append(t)
        return tools
