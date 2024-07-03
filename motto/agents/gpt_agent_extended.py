from openai import OpenAI
from .gpt_agent import ChatGPTAgent
import httpx
import os
import json
from .history_processor import HistoryProcessor

# FIXME: A more flexible was to setup proxy?
proxy = os.environ.get('OPENAI_PROXY')
client = OpenAI() if proxy is None else \
    OpenAI(http_client=httpx.Client(proxies=proxy))

class ChatGPTAgentExtended(ChatGPTAgent):
    '''
    GPT agent with a cut_history parameter to ensure the length of the current context window stays within the model's allowed limit
    '''

    def __init__(self, model="gpt-3.5-turbo", stream=False, cut_history=False,  media_message="", timeout=15, max_response_tokens=512):
        super().__init__(model,stream, timeout)
        self.cut_history = cut_history
        self.max_response_tokens = max_response_tokens
        self.media_message = media_message
        if cut_history:
            self.history_processor = HistoryProcessor(self._model, self.max_response_tokens)

    def __call__(self, messages, functions=[]):
        if self.cut_history:
            messages = self.history_processor.process_dialog_history(messages)
        if self.media_message != "":
            messages.extend(json.loads(self.media_message))

        if functions == []:
            response = client.chat.completions.create(model=self._model,
                                                      messages=messages,
                                                      temperature=0,
                                                      timeout=self.timeout,
                                                      stream=self.stream_response,
                                                      max_tokens=self.max_response_tokens)
            return response.choices[0].message if not self.stream_response else response
        tools = []
        for func in functions:
            dict_values = {}
            dict_values["type"] = "function"
            dict_values["function"] = func
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
