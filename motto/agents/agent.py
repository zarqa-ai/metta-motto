from openai import OpenAI

client = OpenAI()

class FunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class Response:
    def __init__(self, content, function_call):
        self.content = content
        self.function_call = function_call

class EchoAgent:
    def __call__(self, messages, functions):
        msg = list(map(lambda m: m['role'] + ' ' + m['content'], messages))
        msg = '\n'.join(msg)
        fcall = None
        # A mock function call processing for testing purposes
        for f in functions:
            vcall = None
            if f['description'] in msg:
                prop = f['parameters']['properties']
                for k in prop:
                    if 'enum' in prop[k]:
                        for v in prop[k]['enum']:
                            if prop[k]['description'] + v in msg:
                                vcall = {k: v}
                fcall = FunctionCall(f['name'], vcall)
        return Response(msg, fcall)


class ChatGPTAgent:

    def __init__(self, model="gpt-3.5-turbo-0613"):
        self._model = model

    def __call__(self, messages, functions):
        if functions==[]:
            response = client.chat.completions.create(model=self._model,
            messages=messages,
            temperature=0,
            timeout = 15)
        else:
            response = client.chat.completions.create(model=self._model,
            messages=messages,
            functions=functions,
            function_call="auto",
            temperature=0,
            timeout = 15)
        # FIXME? Only one result is supposed now. API can be changed later if it turns out to be needed.
        return response.choices[0].message

