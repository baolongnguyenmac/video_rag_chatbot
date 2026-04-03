from tools.image_tool.video_chunking import VideoChunking

import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from langchain_core.tools import tool, BaseTool

import cv2

class ImageVectorDB:
    def __init__(self, collection_name:str, persist_directory:str):
        chroma_client = chromadb.PersistentClient(path=persist_directory)
        image_loader = ImageLoader()
        embedding_func = OpenCLIPEmbeddingFunction()

        print('Init img database...')
        self.multimodal_db = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_func,
            data_loader=image_loader
        )
        print('~'*80)

    def add_video(self, video_path:str, sub_path:str) -> None:
        print(f'Importing video: {video_path.split("/")[-1]}')
        meta_data = VideoChunking.get_video_chunk(video_path, sub_path)

        ids = [str(hash(md['frame_path'])) for md in meta_data]
        uris = [md['frame_path'] for md in meta_data]
        self.multimodal_db.add(
            ids=ids,
            uris=uris,
            metadatas=meta_data
        )

        print(f'{video_path.split("/")[-1]} imported!')
        print('~'*80)

    def search_img_by_text(self, k:int) -> BaseTool:
        @tool(response_format='content')
        def img_retrieve_by_text(query:str) -> str:
            """retrieve metadata of relevant images based on the given description (input query). this function uses the given description to retrieve relevant images from vector database and return the metadata of relevant images. Metadata of an image contains: path to the image, corresponding subtitle and subtitle duration (start and end timestamp)

            Args:
                query (str): a description to retrieve images

            Returns:
                str: metadata of relevant images
            """
            print(f'[img_retrieve_by_text] Image retrieve with query: {query}')
            reply = self.multimodal_db.query(
                query_texts=query,
                n_results=k,
                include=['distances', 'metadatas']
            )
            print('~'*80)

            return '\n'.join([f'''
PATH: {r['frame_path']}
SUBTITLE: {r['transcript']}
DURATION:
    Start: {r['start']}
    End: {r['end']}
''' for r in reply['metadatas'][0]])

        return img_retrieve_by_text

    def search_img_by_img(self, k:int) -> BaseTool:
        @tool(response_format='content')
        def img_retrieve_by_img(filepath:str) -> str:
            """retrieve metadata of relevant images based on the given image path. this function reads the image from given image path, retrieves relevant images from vector database and return the metadata of relevant images. Metadata of an image contains: path to the image, corresponding subtitle and subtitle duration (start and end timestamp)

            Args:
                filepath (str): path to query image

            Returns:
                str: metadata of relevant images
            """
            print(f'[img_retrieve_by_img] Get relevant file of {filepath}')
            reply = self.multimodal_db.query(
                query_images=cv2.imread(filepath),
                n_results=k,
                include=['distances', 'metadatas']
            )
            print('~'*80)

            return '\n'.join([f'''
PATH: {r['frame_path']}
SUBTITLE: {r['transcript']}
DURATION:
    Start: {r['start']}
    End: {r['end']}
''' for r in reply['metadatas'][0]])

        return img_retrieve_by_img

if __name__=='__main__':
    vector_db = ImageVectorDB(
        collection_name='test',
        persist_directory='./data/test_db'
    )
    vector_db.add_video('./data/video/The Android Tab/The Android Tab.mp4', './data/video/The Android Tab/The Android Tab.srt')
    searcher = vector_db.search_img_by_text(k=3)
    print(searcher('iPhone'))