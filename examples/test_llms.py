import json
import threading
import time
from hyperon import MeTTa
from motto.agents import MettaScriptAgent, DialogAgent
from motto.agents.api_importer import AIImporter
from motto.thread_agents import ListeningAgent
from motto import get_sentence_from_stream_response

import unittest
class TestLLms(unittest.TestCase):
    def test_stream_response(self):
        m = MeTTa()
        # we can run metta code from python directly and motto works
        m.run('!(import! &self motto)')
        result = m.run('!((chat-gpt-agent "gpt-3.5-turbo" True) (user "Who is John Lennon?"))', True)
        assert hasattr(result[0].get_object().content, "__stream__")


    def test_no_stream_response(self):
        m = MeTTa()
        # we can run metta code from python directly and motto works
        m.run('!(import! &self motto)')
        result = m.run('!((chat-gpt-agent "gpt-3.5-turbo" False True) (user "Say meow"))', True)
        assert "meow" in str(result[0].get_object().content).lower()


    def test_chat_gpt_additional_info(self):
        agent = MettaScriptAgent(path="basic_stream_call.msa")
        v = agent('(Messages (system  "You are Grace, you are in London")(user "Say meow"))',
                  additional_info=[("model_name", "gpt-3.5-turbo", 'String'), ("is_stream", False, 'Bool'),
                                   ("media_msg", "", 'String')]).content
        result = v[0].get_object().content
        assert "meow" in result.lower()


    def encode_image(slef,image_path):
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


    def test_chat_gpt_media(self):
        import importlib.util
        if importlib.util.find_spec('base64') is not None:
            base64_image = self.encode_image("data/peace.jpg")
            agent = MettaScriptAgent(path="basic_stream_call.msa")
            media_messages = {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    },
                ],
            }
            media = ('media_msg', json.dumps(media_messages), 'String')
            v = agent('(Messages (system  "You are Grace, you are in London")(user "What do you see on image"))',
                      additional_info=[("system_msg", "please answer with one sentence", 'String'),
                                       ("model_name", "gpt-4o", 'String'), ("is_stream", False, 'Bool'), media]).content
            result = v[0].get_object().content
            assert "dove" in result.lower()


    def test_stream_response_processer(self):
        agent = DialogAgent(code='''
            (= (respond)((chat-gpt-agent "gpt-3.5-turbo" True True) (Messages (history)  (messages))) )
            (= (response) (respond))
        ''')
        agent('(Messages (system  "Who made significant advancements in the fields of electromagnetism?"))')

        for v in agent.process_last_stream_response():
            print(v)


    def test_canceling(self):
        agent = ListeningAgent(code='''
            (= (respond)((chat-gpt-agent "gpt-3.5-turbo" True True) (Messages (history)  (messages))) )
            (= (response) (respond))
        ''')
        agent('(Messages (system  "Who made significant advancements in the fields of electromagnetism?"))')
        time.sleep(3)
        agent.stop()
        assert agent.has_output()

        agent('(Messages (system  "Who made significant advancements in the fields of electromagnetism?"))')

        agent.set_canceling_variable(True)
        time.sleep(3)
        agent.stop()
        assert (not agent.has_output())

    def test_open_router_stream_sentence(self):
        code = '''
            (= (respond)
                ((open-router-agent "openai/gpt-3.5-turbo" True) (messages))
            )
            (= (response) (respond))
        '''
        agent = MettaScriptAgent(code=code)
        v = agent('(Messages (system  "You are Grace, you are in London")(user "Who was the 22nd President of France?"))')
        stream = get_sentence_from_stream_response(v.content)
        for chunk in stream:
            print(chunk)
            assert "president" in chunk.lower()

    def test_chat_gpt_stream_sentence(self):
        code = '''
            (= (respond)
                ((chat-gpt-agent "gpt-3.5-turbo" True) (messages))
            )
              (= (response) (respond))
        '''
        agent = MettaScriptAgent(code=code)
        v = agent('(Messages (system  "You are Grace, you are in London")(user "Who was the 22nd President of France?"))')
        stream = get_sentence_from_stream_response(v.content)
        for chunk in stream:
            print(chunk)
            assert "president" in chunk.lower()

    def test_ai_importer(self):
        # test case when library does not exist
        ai_importer = AIImporter('ChatGPTAgent', 'OPENAI_API_KEY', requirements=['openai_'],
                                 client_constructor='openai.OpenAI', proxy='OPENAI_PROXY')
        with self.assertRaises(RuntimeError) as context:
            cl = ai_importer.client
        assert ai_importer.has_errors() > 0
        self.assertEqual(str(context.exception), f"Install openai_ library to use ChatGPTAgent")

    def test_ai_importer_key(self):
        # test case when api key does not exist
        ai_importer = AIImporter('ChatGPTAgent', key=None, requirements=['openai'],
                                 client_constructor='openai.OpenAI', proxy='OPENAI_PROXY')
        with self.assertRaises(RuntimeError) as context:
            cl = ai_importer.client
        assert ai_importer.has_errors() > 0
        self.assertEqual(str(context.exception), f"Specify key variable for AIImporter to use ChatGPTAgent agents")

    def test_ai_importer_constructor(self):
        ai_importer = AIImporter('ChatGPTAgent', key='OPENAI_API_KEY', requirements=['openai'],
                                 client_constructor=None, proxy='OPENAI_PROXY')

        assert ai_importer.has_errors() == 0
        assert ai_importer.client is None




