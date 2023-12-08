import os
from abc import abstractmethod


class AbstractEmbeddings:
    @abstractmethod
    def get_embeddings(self, text):
        pass

    @abstractmethod
    def get_chunks_embeddings(self, chunks):
        pass


class OpenAIEmbeddings(AbstractEmbeddings):

    def __init__(self, model="text-embedding-ada-002"):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model

    def get_embeddings(self, text):
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def get_chunks_embeddings(self, chunks):
        embeddings = []
        for text in chunks:
            embeddings.append(self.get_embeddings(text))
        return embeddings
