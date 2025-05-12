from motto.agents.api_importer import AIImporter
from .agent import Agent, Response, correct_the_response
import logging
from typing import Any, Dict

ai_importer = AIImporter('LangChainLLmAgent',
                         requirements=['langchain', 'langchain_core.tools','langchain.chat_models',
                                        'langchain_core.messages', 'pydantic'],
                         )


def mock_func():
    return None


def pydantic_model_from_json_schema(name: str, schema: Dict[str, Any]):
    if 'pydantic' not in ai_importer.imported_modules:
        return None
    if schema.get("type") != "object":
        raise ValueError("Only 'object'-type schemas are supported")

    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))

    fields = {}

    for prop_name, prop_schema in properties.items():
        field_type = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }.get(prop_schema.get("type"), Any)

        # Required fields use ..., optional fields use default None
        fields[prop_name] = (field_type, ... if prop_name in required_fields else None)

    return ai_importer.imported_modules['pydantic'].create_model(name, **fields)


class LangChainLLmAgent(Agent):

    def __init__(self, model="gpt-4o-mini", model_provider='openai', stream=False):
        super().__init__()
        ai_importer.check_errors()
        ai_importer.import_library()
        if 'langchain.chat_models' not in ai_importer.imported_modules:
            return
        self.model = ai_importer.imported_modules['langchain.chat_models'].init_chat_model(model,
                                                                                           model_provider=model_provider)
        self.stream = stream
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.model_to_invoke = self.model

    def _collect_tools(self, functions):
        if "langchain_core.tools" not in ai_importer.imported_modules:
            return None
        tools = []
        for func in functions:
            tool = ai_importer.imported_modules["langchain_core.tools"].StructuredTool.from_function(
                name=func["name"],
                description=func["description"],
                args_schema=pydantic_model_from_json_schema("funcInput", func),
                func=mock_func
            )

            tools.append(tool)
        return tools

    def _get_messages(self, messages):
        if "langchain_core.messages" not in ai_importer.imported_modules:
            return []
        result = []
        for m in messages:
            if m['role'] == "system":
                result.append(ai_importer.imported_modules["langchain_core.messages"].SystemMessage(m["content"]))
            elif m["role"] == "user":
                result.append(ai_importer.imported_modules["langchain_core.messages"].HumanMessage(m["content"]))

        return result

    def __call__(self, messages, functions=[]):
        try:
            # self.client = ai_importer.client
            if len(functions) > 0:
                tools = self._collect_tools(functions)
                self.model_to_invoke = self.model.bind_tools(tools)
            langChain_messages = self._get_messages(messages)
            if self.stream:
                response = self.model_to_invoke.stream(langChain_messages)
                return response
            else:
                response = self.model_to_invoke.invoke(langChain_messages)
                return correct_the_response(response)
        except Exception as e:
            return Response(f"Error: {e}")
