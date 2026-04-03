from tools.text_vector_db import TextVectorDB

from langchain_core.documents.base import Document

from shutil import rmtree
import os
from dotenv import load_dotenv
load_dotenv()

class TestTextVectorDB:
    persist_directory='./src/tools/test/text_db'
    collection_name='test_text'
    vector_db = TextVectorDB(
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    filepath = os.path.join(persist_directory, 'test.pdf')
    pdf_url = 'https://arxiv.org/pdf/1912.04977'
    os.system(f'curl -sSL -o {filepath} {pdf_url}')

    def test_add_doc(self):
        self.vector_db.add_doc(self.filepath)

    def test_similarity_search(self):
        query = 'Federated learning'
        k = 10
        relevant_docs = self.vector_db.similarity_search(query, k)

        assert len(relevant_docs) == k
        assert type(relevant_docs) is list
        assert type(relevant_docs[0]) is Document

    def test_remove_collection(self):
        rmtree(self.persist_directory)

if __name__=='__main__':
    tester = TestTextVectorDB()
    tester.test_remove_collection()
