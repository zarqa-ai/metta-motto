from openai import OpenAI
from .agent import Agent
import httpx
import os

# FIXME: A more flexible was to setup proxy?
proxy=os.environ.get('OPENAI_PROXY')
client = OpenAI() if proxy is None else \
         OpenAI(http_client=httpx.Client(proxies=proxy))

class ChatGPTAgent(Agent):

    def __init__(self, model="gpt-3.5-turbo-0613"):
        self._model = model

    def __call__(self, messages, functions=[]):
        if functions == []:
            response = client.chat.completions.create(model=self._model,
                messages=messages,
                temperature=0,
                timeout = 15)
        else:
            tools = []
            for func in functions:
                dict_values = {}
                dict_values["type"] = "function";
                dict_values["function"] = func
                tools.append(dict_values)
            response = client.chat.completions.create(model=self._model,
                messages=messages,
                tools=tools,
                temperature=0,
                tool_choice="auto",
                timeout = 15)
        # FIXME? Only one result is supposed now. API can be changed later if it turns out to be needed.
        return response.choices[0].message
