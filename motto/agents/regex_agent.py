from .agent import Agent
from pathlib import Path
from hyperon import MeTTa, Environment

class RegexAgent(Agent):

    def __init__(self, space_name,  regex_intents_dir, possible_responses_dir, include_paths=None):

        if not (Path.exists(regex_intents_dir)):
            raise AttributeError("Need to provide a path to regex templates")


        if not (Path.exists(possible_responses_dir)):
            raise AttributeError("Need to provide a path to responses for intents")
        self._includes = include_paths

        if self._includes is not None:
            env_builder = Environment.custom_env(include_paths=self._includes)
            self.metta = MeTTa(env_builder=env_builder)
        else:
            self.metta = MeTTa()

        regex_templates = Path(regex_intents_dir)
        for template in regex_templates.iterdir():
            self.metta.run(f"!(import! &{space_name} {template})")

        regex_templates = Path(possible_responses_dir)
        for template in regex_templates.iterdir():
            self.metta.run(f"!(import! &{space_name} {template})")



    def __call__(self, messages, functions=[], doc_name=[]):
        if isinstance(messages, str):
            text = messages
        else:
            try:
                text = list(map(lambda m: m['content'], messages))
                text = '\n'.join(text)
            except Exception as ex:
                raise TypeError(f"Incorrect argument for retrieval-agent: {ex}")


        embeddings_values = self.embeddings_getter.get_embeddings(text)
        if not doc_name:
            context = self.collection.query(query_embeddings=embeddings_values, n_results=self.docs_count)
        else:
            if self.data_source not in doc_name:
                doc_name = os.path.join(self.data_source, doc_name)
            context = self.collection.query(query_embeddings=embeddings_values, n_results=self.docs_count,
                                            where={"source": doc_name})
        docs = context["documents"][0]
        res = ""
        for doc in docs:
            next = doc.replace('"', "'")
            if next not in res:
                res += next + "\n"
