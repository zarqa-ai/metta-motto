import anthropic
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

from motto.agents.langchain_tools import LangchainTools
from .agent import Agent, Response
import httpx
import os
import logging
from langchain_openai import ChatOpenAI

# FIXME: A more flexible was to setup proxy?
proxy = os.environ.get('OPENAI_PROXY')
client = anthropic.Anthropic() if proxy is None else \
    anthropic.Anthropic(http_client=httpx.Client(proxies=proxy))


def get_system(messages):
    return "\n".join(m["content"] for m in messages if m["role"] == "system")


def get_messages_no_system(messages):
    return [m for m in messages if m["role"] != "system"]


class OpenAIToolsAgent(Agent):
    def __init__(self, tools, model="gpt-3.5-turbo-1106"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.tools = tools.split(';') if ';' in tools else [tools]
        self.tools = [LangchainTools.get_tool_by_name(tool) for tool in self.tools]

    def __call__(self, messages, functions=[]):
        input = ""
        for message in messages[::-1]:
            if message['role'] == 'user':
                input = message['content']
        prompt = ChatPromptTemplate.from_messages([
            ("system", "ou are a helpful assistant"),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name='agent_scratchpad')])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        response = agent_executor.invoke({"input": input})
        return Response(response['output'])
