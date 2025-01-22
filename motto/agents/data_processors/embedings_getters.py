from abc import abstractmethod

from motto.agents.api_importer import AIImporter


class AbstractEmbeddings:
    @abstractmethod
    def get_embeddings(self, text):
        pass

    @abstractmethod
    def get_chunks_embeddings(self, chunks):
        pass


class OpenAIEmbeddings(AbstractEmbeddings):

    def __init__(self, model="text-embedding-ada-002"):
        self.ai_importer = self.ai_importer = AIImporter('ChatGPTAgent', 'OPENAI_API_KEY', requirements=['openai'],
                                                         client_constructor='openai.OpenAI', proxy='OPENAI_PROXY')
        self.client = self.ai_importer.get_ai_client()
        self.model = model

    def get_embeddings(self, text):
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def get_chunks_embeddings(self, chunks):
        embeddings = []
        for text in chunks:
            embeddings.append(self.get_embeddings(text))
        return embeddings
