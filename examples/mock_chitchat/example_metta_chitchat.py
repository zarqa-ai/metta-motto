import logging

from hyperon.exts.agents.events.basic_bus import BasicEventBus

from examples.mock_chitchat.caller_args_getter import CallerArgsGetter
from examples.mock_chitchat.motto_chit_chat import MottoChitChatAgent
from examples.mock_chitchat.mock_auto_conv_history import MockAutoConvHistory
from examples.mock_chitchat.mock_config import MockConfig
#from examples.mock_chitchat.mock_image_handler import MockImageHandler
from examples.mock_chitchat.mock_stt import MockSTT
from examples.mock_chitchat.mock_tts_interface_waci import MockTTSInterfaceWACI

logging.basicConfig(level=logging.INFO)


# Initialize mock enviroment
config = MockConfig("config.yaml")
commands_config = {"simple_say": {}, "directed_say" : {}}
# if config.get("chitchat.enable_vision"):
#     image_handler = MockImageHandler()
# else:
image_handler = None

node = BasicEventBus()
stt = MockSTT(node)
#tts_waci = MockTTSInterfaceWACI(node)
#auto_history = MockAutoConvHistory(node)

# After this point your can use mock environment
# You should use three classes:
# tts_waci - TTS interface with automatic canceling and interruption
# auto_history - class for automatic collection of conversation history from TTS
# image_handler - image handler
# You should subscribe for two topics using node.create_subscription:
#     - "/stt/sentence_topic" to get sentences from STT
#     - "/chitchat/command_topic" to get chitchat commands
# You should use:
# stt.publish_realtime function to simulate receiving sentence via STT approximately in realtime with all corresponding events
# stt.publish_direct function to directly send sentence to "/stt/sentence_topic" (simulation of user typing something in GUI)
args_getter = CallerArgsGetter(config, image_handler)
metta_agent = MottoChitChatAgent(path="simple_call_.msa", event_bus=node,
                                 args_getter=args_getter, config=config, commands_config=commands_config)

metta_agent.start()

while True:
    s = input().strip()
    if s.startswith(":"): # it is command, we publish it immediatly
        stt.publish_direct(s)
    else:
        stt.publish_realtime(s)
