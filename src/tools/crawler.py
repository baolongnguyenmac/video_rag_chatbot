from tools.text_vector_db import TextVectorDB
from tools.img_vector_db import ImageVectorDB
from tools.video_chunking import VideoChunking

from langchain_core.tools import tool, BaseTool

class Crawler:
    def __init__(self, text_vector_db:TextVectorDB, img_vector_db:ImageVectorDB):
        self.text_vector_db = text_vector_db
        self.img_vector_db = img_vector_db

    def get_crawler(self) -> BaseTool:
        @tool(response_format='content')
        def crawl(url:str)-> str:
            """this tool downloads a YouTube video (video and subtitle) based on given url, then embed them into 2 vector database (text vector database for subtitle and image vector database for frames in video) and return a success message

            Args:
                url (str): an URL of a YouTube video

            Returns:
                str: a success message
            """
            video_path, sub_path = VideoChunking.download_url(url)
            self.text_vector_db.add_sub(sub_path)
            self.img_vector_db.add_video(video_path, sub_path)

            return "Download and embed video successfully"

        return crawl