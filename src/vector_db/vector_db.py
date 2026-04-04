import chromadb
from chromadb.utils.embedding_functions import GoogleGeminiEmbeddingFunction

class VectorDB:
    def __init__(self, persist_directory:str):
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)

    def get_collection(self, collection_name:str):
        return self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=GoogleGeminiEmbeddingFunction(
                model_name="gemini-embedding-2-preview",
                task_type="RETRIEVAL_DOCUMENT",
            )
        )

    '''
    index_img
    index_text
    wrapper(index_img, index_text) --> tool

    search(img) --> tool
    search(text) --> tool
    '''

    def add_imgs(self, collection_name:str, meta_data:list[dict]):
        collection = self.get_collection(collection_name)

        ids = [str(hash(md['frame_path'])) for md in meta_data]
        uris = [md['frame_path'] for md in meta_data]
        collection.add(
            ids=ids,
            uris=uris,
            metadatas=meta_data
        )

    def add_subtitle(self, collection_name:str, subtitle:list[str]):
        pass

if __name__=='__main__':
    
