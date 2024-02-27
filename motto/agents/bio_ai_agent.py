import os

from .agent import Response

from .metta_agent import MettaAgent
from hyperon import MeTTa, Environment, E, S


def repr_atom(atom) -> str:
    item = repr(atom)
    if len(item) > 2 and item[0] == '"' and item[-1] == '"':
        item = item[1:-1]
    return item

class BioAIAgent(MettaAgent):

    def __init__(self,  data_folder=None, path=None, include_paths=None):
        self._data_folder = self._try_unwrap(data_folder)
        self._path = self._try_unwrap(path)
        if data_folder is None:
            raise RuntimeError(f"{self.__class__.__name__} requires path to  data")
        if path is None:
            raise RuntimeError(f"{self.__class__.__name__} requires path to instructions")
        self._includes = include_paths

        if self._includes is not None:
            env_builder = Environment.custom_env(include_paths=self._includes)
            self.metta = MeTTa(env_builder=env_builder)
        else:
            self.metta = MeTTa()

        if os.path.isfile(self._data_folder):
            files = [self._data_folder]
        else:
            files= []
            for path, subdirs, files_ in os.walk(self._data_folder):
                for name in files_:
                    files.append(os.path.join(path, name))
            #files = [os.path.join(self._data_folder, file) for file in os.listdir(self._data_folder)]
        self.space_name = "space"
        self.metta.run(f"!(bind! &{self.space_name} (new-space))")
        for file in files:
            self.metta.run(f"!(load-ascii &{self.space_name} {file})")




    def _prepare(self, metta, msgs_atom):
        metta.space().add_atom(E(S('='), E(S('messages')), msgs_atom))

    def __call__(self, msgs_atom, functions=[]):
        # FIXME: we cannot use higher-level metta here (e.g. passed by llm func),
        # from which an agent can be called, because its space will be polluted.
        # Thus, we create new metta runner and import motto.
        # We could avoid importing motto each time by reusing tokenizer or by
        # swapping its space with a temporary space, but current API is not enough.
        # It could also be possible to import! the agent script into a new space,
        # but there is no function to do this without creating a new token
        # (which might be useful). The latter solution will work differently.
        if self._includes is not None:
            env_builder = Environment.custom_env(include_paths=self._includes)
            metta = MeTTa(env_builder=env_builder)
        else:
            metta = MeTTa()
        metta.run("!(import! &self motto)")
        if isinstance(msgs_atom, str):
            msgs_atom = metta.parse_single(msgs_atom)
        self._prepare(metta, msgs_atom)
        response = []
        if self._path is not None:
            # response = metta.load_module_at_path(self._path)
            with open(self._path, mode='r') as f:
                code = f.read()
                query = metta.run(code, True)
                if len(query) == 1:
                    query = repr_atom(query[0])
                    query = query.replace("&self", f"&{self.space_name}")
                    print(query)
                    response = self.metta.run("!"+query, True)

        return Response(response, None)
