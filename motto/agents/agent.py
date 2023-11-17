import openai


class EchoAgent:
    def __call__(self, messages, functions):
        msg = list(map(lambda m: m['role'] + ' ' + m['content'], messages))
        return {'content': '\n'.join(msg)}


class ChatGPTAgent:

    def __init__(self, model="gpt-3.5-turbo-0613"):
        self._model = model

    def __call__(self, messages, functions):
        if functions==[]:
            response = openai.ChatCompletion.create(
                model=self._model,
                messages=messages,
                temperature=0,
                timeout = 15)
        else:
            response = openai.ChatCompletion.create(
                model=self._model,
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0,
                timeout = 15)
        # FIXME? Only one result is supposed now. API can be changed later if it turns out to be needed.
        return response["choices"][0]["message"]

