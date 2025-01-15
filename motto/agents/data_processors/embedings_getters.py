import importlib.util
import os
from abc import abstractmethod

from motto.utils import get_ai_client


class AbstractEmbeddings:
    @abstractmethod
    def get_embeddings(self, text):
        pass

    @abstractmethod
    def get_chunks_embeddings(self, chunks):
        pass


class OpenAIEmbeddings(AbstractEmbeddings):

    def __init__(self, model="text-embedding-ada-002"):
        if importlib.util.find_spec('openai') is not None:
            from openai import OpenAI
        else:
            raise RuntimeError("Install OpenAI library to use OpenAI agents")

        proxy = os.environ.get('OPENAI_PROXY')
        self.client = get_ai_client(OpenAI, proxy)
        self.model = model

    def get_embeddings(self, text):
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def get_chunks_embeddings(self, chunks):
        embeddings = []
        for text in chunks:
            embeddings.append(self.get_embeddings(text))
        return embeddings
