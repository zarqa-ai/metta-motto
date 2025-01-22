from .agent import Response, Agent, EchoAgent, atom2msg
from .metta_agent import MettaScriptAgent, MettaAgent, DialogAgent
from .gpt_agent import ChatGPTAgent
from .openrouter_agent import OpenRouterAgent
import importlib.util
from .anthropic_agent import AnthropicAgent
from .retrieval_agent import RetrievalAgent

# if importlib.util.find_spec('anthropic') is not None:
#
