from openai import OpenAI
from .agent import Agent
import httpx
import os
import tiktoken

# FIXME: A more flexible was to setup proxy?
proxy = os.environ.get('OPENAI_PROXY')
client = OpenAI() if proxy is None else \
    OpenAI(http_client=httpx.Client(proxies=proxy))


def get_max_tokens(model_name):
    if model_name == "gpt-3.5-turbo":
        return 10000  # real limit 16385
    if model_name == "gpt-4-turbo-preview":
        return 10000  # Limit max number of tokens to reduce cost (real limit 128000)
    if model_name == "gpt-4-turbo":
        return 10000  # Set max number of tokens to reduce cost (real limit 128000)
    raise Exception("Unknown model name")


class HistoryProcessor:

    def __init__(self, model_name,  max_response_tokens):
        self.model_name = model_name
        self.max_tokens = get_max_tokens(self.model_name) -  max_response_tokens
        # we need tokenizer only to calculate number of tokens and cut dialog history if needed
        self.encoder = tiktoken.encoding_for_model(self.model_name)

    def num_tokens_for_single_message(self, m):
        # will work for all models except outdated gpt-3.5-turbo-0301
        tokens_per_message = 3  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        # tokens_per_name = 1  # if there's a name, the role is omitted
        num_tokens = tokens_per_message
        for key, value in m.items():
            num_tokens += len(self.encoder.encode(value))
            # if key == "name":
            #     num_tokens += tokens_per_name
        return num_tokens

    def process_dialog_history(self, messages):

        # remove old history in order to fit into the prompt
        lines_tokens = [self.num_tokens_for_single_message(m) for m in messages]
        sum_tokens = 0
        i_cut = 0
        for i in reversed(range(len(lines_tokens))):
            sum_tokens += lines_tokens[i]
            if sum_tokens > self.max_tokens:
                i_cut = i + 1
                break
        if i_cut > 0:
            messages = messages[i_cut:]

        # todo add image

        # # Add image if received
        # if self.image_handler is not None and self.image_handler.image is not None:
        #     messages = self.insert_image(messages)
        return messages


class ChatGPTAgentExtended(Agent):
    '''
    GPT agent with a cut_history parameter to ensure the length of the current context window stays within the model's allowed limit
    '''

    def __init__(self, model="gpt-3.5-turbo", stream=False, cut_history=False, timeout=15, max_response_tokens=512):
        self._model = model
        self.stream_response = stream
        self.cut_history = cut_history
        self.timeout = timeout
        self.max_response_tokens = max_response_tokens
        if cut_history:
            self.history_processor = HistoryProcessor(self._model, self.max_response_tokens)

    def __call__(self, messages, functions=[]):
        if self.cut_history:
            messages = self.history_processor.process_dialog_history(messages)

        if functions == []:
            response = client.chat.completions.create(model=self._model,
                                                      messages=messages,
                                                      temperature=0,
                                                      timeout=self.timeout,
                                                      stream=self.stream_respons,
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
