from abc import abstractmethod

from motto.agents.api_importer import AIImporter
ai_importer = AIImporter('ChatGPTAgent', 'OPENAI_API_KEY', requirements=['openai'],
                                                         client_constructor='openai.OpenAI', proxy='HTTP_PROXY')

class AbstractEmbeddings:
    @abstractmethod
    def get_embeddings(self, text):
        pass

    @abstractmethod
    def get_chunks_embeddings(self, chunks):
        pass


class OpenAIEmbeddings(AbstractEmbeddings):

    def __init__(self, model="text-embedding-ada-002"):

        self.client = ai_importer.client
        self.model = model

    def get_embeddings(self, text):
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def get_chunks_embeddings(self, chunks):
        embeddings = []
        for text in chunks:
            embeddings.append(self.get_embeddings(text))
        return embeddings
