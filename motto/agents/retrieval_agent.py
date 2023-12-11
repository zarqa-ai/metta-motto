import shutil

import chromadb
import numpy as np
import os
import pathlib
import concurrent.futures

from agents import Agent
from agents.agent import Response
from agents.data_processors import OpenAIEmbeddings, DocProcessor
from hyperon import *


def fix_string(value):
    if len(value) > 1 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value
class RetrievalAgent(Agent):
    max_length = 2270
    def __init__(self, data_source, chunk_token_size, data_dir):

        if isinstance(data_source, GroundedAtom):
            data_source = fix_string(repr(data_source))
        if not (os.path.isfile(data_source) or os.path.isdir(data_source)):
            raise AttributeError("data_source should be file or folder")

        if not os.path.exists(data_source):
            return
        if isinstance(chunk_token_size, GroundedAtom):
            chunk_token_size = int(repr(chunk_token_size))

        if isinstance(data_dir, GroundedAtom):
            data_dir = fix_string(repr(data_dir))


        self.chunk_token_size = chunk_token_size
        self.embeddings_getter = OpenAIEmbeddings()
        # data source can be a single file or a folder with files
        self.data_source = data_source
        # the database is named as data_source
        db_name = pathlib.Path(self.data_source).stem
        self.db = os.path.join(data_dir, f"{db_name}_embedings")
        self.collection_name = f"{db_name}_collection"
        need_load_docs = not os.path.exists(self.db)
        self.chroma_client = chromadb.PersistentClient(self.db)
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name,
                                                                      metadata={"hnsw:space": "cosine"})

        if not need_load_docs:
            if self.collection.count() == 0:
                need_load_docs = True
                shutil.rmtree(self.db)

        if need_load_docs:
            self._load_docs()

    def _process_doc(self, file):
        chunks = {}
        text = DocProcessor.clear_text(file)
        chunks['texts'] = DocProcessor.get_text_chunks(text, self.chunk_token_size)
        chunks['embeddings'] = self.embeddings_getter.get_chunks_embeddings(chunks['texts'])
        length = len(chunks['texts'])
        if length > 0:
            chunks['source'] = [{'source': file}] * length
        return chunks

    def _load_docs(self):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                if os.path.isfile(self.data_source):
                    files = [self.data_source]
                else:
                    files = [os.path.join(self.data_source, file) for file in  os.listdir(self.data_source)]
                for file in files:
                    futures.append(executor.submit(self._process_doc, file=file))
                i = 0
                for future in concurrent.futures.as_completed(futures):
                    chunks = future.result()
                    length = len(chunks['texts'])
                    chunks['ids'] = [f"id{i + j}" for j in range(length)]
                    i += length
                    self.collection.add(embeddings=chunks['embeddings'], documents=chunks['texts'],
                                        metadatas=chunks['source'], ids=chunks['ids'])
        except Exception as ex:
            if os.path.exists(self.db):
                shutil.rmtree(self.db)
            raise RuntimeError(f"RetrievalAgent.__load_docs error: {ex}")

    def __call__(self, messages, docs_count=10):
        if isinstance(messages, str):
            text = messages
        else:
            try:
                text = list(map(lambda m: m['content'], messages))
                text = '\n'.join(text)
            except Exception as ex:
                raise TypeError(f"Incorrect argument for retrieval-agent: {ex}")
        embeddings_values = self.embeddings_getter.get_embeddings(text)
        context = self.collection.query(query_embeddings=embeddings_values, n_results=docs_count)
        docs = context["documents"][0]
        res = ""
        prev = ""
        for doc in docs:
            next = doc.replace('"',"'")
            if next not in res:
                res += next + "\n"

        return Response(f"\"{res}\"", None)

