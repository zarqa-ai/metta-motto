from motto.agents.agent import correct_the_response, Response
from motto.agents.api_importer import AIImporter
from .metta_agent import Agent
import json
ai_importer = AIImporter('OpenRouterAgent', key='OPENROUTER_API_KEY', requirements=['requests'])


class OpenRouterAgent(Agent):
    '''
    OpenRouter is a unified interface for LLMs, this agent use OpenRouter API to get responses from LLM
    '''

    def __init__(self, model="openai/gpt-3.5-turbo", stream=False):
        super().__init__()

        self._model = model
        self.stream_response = stream

    def __call__(self, messages, functions=[]):
        try:
            ai_importer.check_errors()
            data = {
                "model": self._model,
                "messages": messages,
            }
            if functions:
                tools = []
                for func in functions:
                    dict_values = {}
                    dict_values["type"] = "function"
                    dict_values["function"] = func
                    tools.append(dict_values)

                data["tools"] = tools
            else:
                data["stream"] = self.stream_response
            ai_importer.import_library()
            response = ai_importer.imported_modules['requests'].post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {ai_importer.key}",
                },
                data=json.dumps(data)
            )

            if self.stream_response and not functions:
                return response

            result = json.loads(response.content)
            response_message = result['choices'][0]['message']
            if not functions:
                return Response(response_message['content'], role=response_message['role'])
            return correct_the_response(response_message)
        except Exception as e:
            return Response(e, role="system")

