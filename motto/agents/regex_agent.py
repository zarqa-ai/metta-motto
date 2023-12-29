from .agent import Agent, Response
from pathlib import Path
from hyperon import MeTTa, Environment
import random


class RegexAgent(Agent):

    def __init__(self, regex_intents_dir, possible_responses_dir, include_paths=None):

        regex_templates_dir = Path(regex_intents_dir)
        if not (regex_templates_dir.exists()):
            raise AttributeError("Need to provide a path to regex templates")

        possible_responses_dir = Path(possible_responses_dir)
        if not (possible_responses_dir.exists()):
            raise AttributeError("Need to provide a path to responses for intents")

        if not regex_templates_dir.is_dir():
            regex_templates_dir = regex_templates_dir.parent
        if not possible_responses_dir.is_dir():
            possible_responses_dir = possible_responses_dir.parent

        self._includes = include_paths
        # this name could be passed to function , but I do not know will we need it
        self.space_name = "resp"

        if self._includes is not None:
            env_builder = Environment.custom_env(include_paths=self._includes)
            self.metta = MeTTa(env_builder=env_builder)
        else:
            self.metta = MeTTa()

        for template in regex_templates_dir.iterdir():
            self.metta.run(f"!(import! &self {template})")

        for template in possible_responses_dir.iterdir():
            self.metta.run(f"!(import! &{self.space_name} {template})")

        self.metta.run("(= (get-intent-name (Intent $x)) $x)")

    def __call__(self, messages, functions=[], doc_name=[]):
        if isinstance(messages, str):
            text = messages
        else:
            try:
                text = list(map(lambda m: m['content'], messages))
                text = '\n'.join(text)
            except Exception as ex:
                raise TypeError(f"Incorrect argument for retrieval-agent: {ex}")

        responses = self.metta.run(f'''!(let $intent  (get-intent-name (intent "{text}") )
                             (match &{self.space_name} ((Intent $intent)(response $x)) $x))''', True)
        res = ''
        if len(responses) > 0:
            res = random.sample(responses, 1)[0]
        return Response(f"{res}", None)
