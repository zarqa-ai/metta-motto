import importlib.util
if importlib.util.find_spec('openai') is not None:
    from openai import OpenAI
else:
    raise RuntimeError("Install OpenAI library to use OpenAI agents")

from .metta_agent import Agent

import os
from .messages_processor import MessagesProcessor
from motto.utils import get_ai_client

# FIXME: A more flexible was to setup proxy?
proxy = os.environ.get('OPENAI_PROXY')
key = os.environ.get('OPENAI_API_KEY')
client = None
if key is not None:
    client = get_ai_client(OpenAI, proxy)
else:
    raise RuntimeError("Specify OPENAI_API_KEY environment variable to use OpenAI agents")

class ChatGPTAgent(Agent):
    '''
    GPT agent with a cut_history parameter to ensure the length of the current context window stays within the model's allowed limit
    '''

    def __init__(self, model="gpt-3.5-turbo", stream=False, cut_history=False,  timeout=15, max_response_tokens=512):
        super().__init__()
        self._model = model
        self.stream_response = stream
        self.timeout = timeout
        self.max_response_tokens = max_response_tokens
        self.messages_processor = MessagesProcessor(self._model, self.max_response_tokens, cut_history)

    def __call__(self, messages, functions=[]):
        messages = self.messages_processor.process_messages(messages)

        if client is None:
            raise RuntimeError("Specify OPENAI_API_KEY environment variable to use OpenAI agents")

        if not functions:
            response = client.chat.completions.create(model=self._model,
                                                      messages=messages,
                                                      temperature=0,
                                                      timeout=self.timeout,
                                                      stream=self.stream_response,
                                                      max_tokens=self.max_response_tokens)
            return response.choices[0].message if not self.stream_response else response
        tools = []
        for func in functions:
            dict_values = {"type": "function", "function": func}
            tools.append(dict_values)
        response = client.chat.completions.create(model=self._model,
                                                  messages=messages,
                                                  tools=tools,
                                                  temperature=0,
                                                  tool_choice="auto",
                                                  timeout=self.timeout,
                                                  max_tokens=self.max_response_tokens)
        # FIXME? Only one result is supposed now. API can be changed later if it turns out to be needed.
        return response.choices[0].message
