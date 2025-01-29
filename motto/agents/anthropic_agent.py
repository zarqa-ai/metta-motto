from motto.agents.api_importer import AIImporter
from .agent import Agent, Response
import logging
import time
ai_importer = AIImporter('AnthropicAgent', key='ANTHROPIC_API_KEY', requirements=['anthropic'],
                                      client_constructor='anthropic.Anthropic', proxy='HTTP_PROXY')

# FIXME: A more flexible was to setup proxy?
class AnthropicAgent(Agent):

    def __init__(self, model="claude-3-opus-20240229"):
        super().__init__()
        self._model = model
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.client = None

    def run_insists(self, **kwargs):
        response = None
        while response is None:
            try:
                response = self.client.messages.create(**kwargs)
            except Exception as e:
                self.log.debug(f"Error: {e}")
                self.log.debug(f"Error: {type(e)}")
                self.log.debug("RETRY!")
                time.sleep(1)
        return response

    def __call__(self, messages, functions=[]):
        try:
            self.client = ai_importer.client
            if not functions:
                response = self.run_insists(model=self._model,
                                            messages=get_messages_no_system(messages),
                                            system=get_system(messages),
                                            max_tokens=1024,
                                            temperature=0,
                                            timeout=15)
            else:
                raise Exception("We do not support functional calls with Anthropic models")
            return Response(response.content[0].text)
        except Exception as e:
            return Response(f"Error: {e}")


def get_system(messages):
    return "\n".join(m["content"] for m in messages if m["role"] == "system")


def get_messages_no_system(messages):
    return [m for m in messages if m["role"] != "system"]
