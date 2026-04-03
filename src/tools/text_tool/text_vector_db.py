from tools.text_tool.text_chunking import TextChunking

# embedding and storing
import chromadb
from langchain_core.documents.base import Document

# tool
from langchain_core.tools import tool, BaseTool

from dotenv import load_dotenv

class TextVectorDB:
    def __init__(self, collection_name:str, persist_directory:str) -> None:
        print('Init text database...')
        self.vector_store = 
        self.vector_store:Chroma = Chroma(
            collection_name=collection_name,
            embedding_function=GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview"),
            persist_directory=persist_directory
        )
        print('~'*80)

    def add_doc(self, filepath:str) -> None:
        print(f'Importing document: {filepath.split("/")[-1]}')
        chunks:list[Document] = TextChunking.get_pdf_chunk(filepath)

        # hash content of chunk to obtain an unique id
        ids = [str(hash(doc.page_content)) for doc in chunks]
        self.vector_store.add_documents(documents=chunks, ids=ids)

        print(f'{filepath.split("/")[-1]} imported!')
        print('~'*80)

    def add_sub(self, filepath:str) -> None:
        print(f'Importing subtitle: {filepath.split("/")[-1]}')
        chunks:list[Document] = TextChunking.get_subtitle_chunk(filepath)

        # hash content of chunk to obtain an unique id
        ids = [str(hash(doc.page_content)) for doc in chunks[:3]]
        self.vector_store.add_documents(documents=chunks[:3], ids=ids)

        print(f'{filepath.split("/")[-1]} imported!')
        print('~'*80)

    def similarity_search(self, query:str, k:int) -> list[Document]:
        return self.vector_store.similarity_search(query=query, k=k)

    def get_text_db_searcher(self, k:int) -> BaseTool:
        """return a semantic search tool that searches for relevant documents in vector db with a given query

        Args:
            k (int): number of return documents

        Returns:
            retrieve: a function
        """

        @tool(response_format='content_and_artifact')
        def text_retrieve(query:str) -> tuple[str, list[Document]]:
            """Search for relevant contents in vector database with a given query

            Args:
                query (str): Query

            Returns:
                content (str): A string of relevant content
                relevant_docs (list[Document]): a list of relevant documents
            """
            print(f'[text_retrieve] Query: {query}')
            relevant_docs = self.vector_store.similarity_search(query=query, k=k)
            content = '\n\n'.join([doc.page_content for doc in relevant_docs])
            print('~'*80)
            return content, relevant_docs

        return text_retrieve

if __name__=='__main__':
    load_dotenv()
    text_vector_db = TextVectorDB('test', './data/db')
    text_vector_db.add_sub('./data/video/The Android Tab/The Android Tab.json')

    print('\n'.join(text_vector_db.vector_store.similarity_search('Iphone', k=3)))
