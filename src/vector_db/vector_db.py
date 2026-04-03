import chromadb
from chromadb.utils.embedding_functions import GoogleGeminiEmbeddingFunction

class VectorDB:
    def __init__(self, collection_name:str, persist_directory:str):
        chroma_client = chromadb.PersistentClient(path=persist_directory)

        self.multimodal_db = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=GoogleGeminiEmbeddingFunction(
                model_name="gemini-embedding-2-preview",
                task_type="RETRIEVAL_DOCUMENT",
            ),
        )

    '''
    index_img
    index_text
    wrapper(index_img, index_text) --> tool

    search(img) --> tool
    search(text) --> tool
    '''

    def add_img(self, img_path:str):

