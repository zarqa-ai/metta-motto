import chromadb
from data_retrivals.doc_processor import DocProcessor
from embedings_getters import OpenAIEmbeddings
import os
import pathlib
import concurrent.futures



class RetrievalAgent:
    def __init__(self, files_folder):
        if not os.path.exists(files_folder):
            return
        self.embeddings_getter = OpenAIEmbeddings()
        self.__original_docs_folder = files_folder
        # we will store database in folder with name "data" in root directory of lib
        parent_dir = pathlib.Path(__file__).parent.resolve().parent.parent
        data_dir = os.path.join(parent_dir, "data")
        # the database is named as files directory
        folder = os.path.basename(files_folder)
        db = os.path.join(data_dir, f"{folder}_embedings")
        self.collection_name = f"{folder}_collection"
        need_load_docs = not os.path.exists(db)
        self.chroma_client = chromadb.PersistentClient(db)
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name,
                                                                      metadata={"hnsw:space": "cosine"})

        if not need_load_docs:
            if self.collection.count() == 0:
                need_load_docs = True
                shutil.rmtree(db)

        if need_load_docs:
            self.__load_docs()

    def __process_doc(self, file):
        chunks = {}
        text = DocProcessor.clear_text(file)
        chunks['texts'] = DocProcessor.get_text_chunks(text)
        chunks['embeddings'] = self.embeddings_getter.get_chunks_embeddings(chunks['texts'])
        length = len(chunks['texts'])
        if length > 0:
            chunks['source'] = [{'source': file}] * length
        return chunks

    def __load_docs(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for file in os.listdir(self.__original_docs_folder):
                futures.append(
                    executor.submit(self.__process_doc, file=os.path.join(self.__original_docs_folder, file))
                )
            i = 0
            for future in concurrent.futures.as_completed(futures):
                chunks = future.result()
                length = len(chunks['texts'])
                chunks['ids'] = [f"id{i + j}" for j in range(length)]
                self.collection.add(embeddings=chunks['embeddings'], documents=chunks['texts'],
                                    metadatas=chunks['source'], ids=chunks['ids'])


if __name__ == '__main__':
    agent = RetrievalAgent("/media/sveta/hdisk4/singnet/texts")
