from tools.text_vector_db import TextVectorDB
from tools.img_vector_db import ImageVectorDB
from tools.crawler import Crawler
from chatbot import ChatBot

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

import time
import gradio as gr
from dotenv import load_dotenv


class ChatRAG(ChatBot):
    def __init__(self, persist_directory:str, text_collection_name:str='text_collection', img_collection_name:str='img_collection'):
        super().__init__()
        self.text_vector_db = TextVectorDB(text_collection_name, persist_directory)
        self.img_vector_db = ImageVectorDB(img_collection_name, persist_directory)
        self.crawler = Crawler(self.text_vector_db, self.img_vector_db)

    def init_graph(self):
        sys_prompt = '''
ROLE: You are a helpful question-answering chatbot that performs the task based on the provided context

CONTEXT: You have the following abilities:
    - Download the YouTube video based on a given URL
    - Split the video into text chunks (which contain subtitle of the video) and image chunks (which contains the frames from the video) to embed into vector databases
    - Query to these databases with text-like and image-like queries to get the needed information
    - These above abilities can be achieved via provided tools

TOOLS:
    - `crawl`: Download and embed video, subtitle into image and text vector database. Input is an YouTube URL
    - `text_retrieve`: Query the subtitle. input is a string
    - `img_retrieve_by_img`: Query the image using. Input is a path to the query image
    - `img_retrieve_by_text`: Query the image. input is a description to search for images

TASK: Do your best to answer user questions
'''

        memory = MemorySaver()
        return create_react_agent(
            model=self.llm,
            tools=[
                self.crawler.get_crawler(),
                self.text_vector_db.get_text_db_searcher(k=5),
                self.img_vector_db.search_img_by_text(k=5),
                self.img_vector_db.search_img_by_img(k=5),
            ],
            checkpointer=memory,
            prompt=SystemMessage(sys_prompt)
        )

    def chat_gradio(self, config:dict):
        graph = self.init_graph()

        def add_message(history:list[dict], message:dict):
            has_file = False
            for filepath in message["files"]:
                has_file = True
                history.append({"role": "user", "content": {"path": filepath}})

            if message["text"] != '':
                history.append({"role": "user", "content": message['text']})

            # if has_file, we have to wait for it to be loaded in db
            return history, gr.MultimodalTextbox(value=None, interactive=has_file)

        def get_reply(history: list):
            # print('~'*80)
            # [print(h, '\n') for h in history]
            # print('~'*80)

            latest_content = history[-1]['content']
            # check if the previous of latest_content is a file
            if type(latest_content) is not tuple:
                try:
                    pre_latest_content = history[-2]
                    if pre_latest_content['role']=='user' and type(pre_latest_content['content']) is tuple:
                        latest_content = ' '.join([latest_content, str(pre_latest_content['content'])])
                except:
                    pass
            # print(latest_content)

            bot_message = graph.invoke(input={"messages": HumanMessage(latest_content)}, config=config)
            bot_message = bot_message['messages'][-1].content

            # streaming answer
            history.append({"role": "assistant", "content": ""})
            for character in bot_message:
                history[-1]["content"] += character
                time.sleep(0.01)
                yield history

        with gr.Blocks(theme='gstaff/xkcd', title='ChatBot', fill_height=True) as demo:
            gr.Markdown("<h1 style='text-align: center;'>NBLong's Assistant</h1>")

            chat_output = gr.Chatbot(elem_id="chatbot", type="messages", scale=1, label='Output')
            chat_input = gr.MultimodalTextbox(
                interactive=True,
                file_count="multiple",
                placeholder="Enter message or upload an image",
                show_label=False,
                sources=["upload"],
                file_types=['image'],
                scale=0
            )

            chat_msg = chat_input.submit(add_message, [chat_output, chat_input], [chat_output, chat_input])
            bot_msg = chat_msg.then(get_reply, chat_output, chat_output, api_name="bot_response")
            bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

        demo.launch(server_name="0.0.0.0", server_port=7860)
        print()

if __name__=='__main__':

    load_dotenv()
    config = {"configurable": {"thread_id": "chatbot_2"}}

    chat_search = ChatRAG(persist_directory='./data/db')
    # # url = 'https://www.youtube.com/watch?v=alDhOLhbkbY' # Vấn Đề Máy Tính Bảng Android
    # url = "https://www.youtube.com/watch?v=xnaD6J-Tl1k&list=RDxnaD6J-Tl1k&start_radio=1&ab_channel=YuchenDuan%28Sandy%29"
    # video_path, sub_path = VideoChunking.download_url(url)
    # chat_search.text_vector_db.add_sub(sub_path)
    # chat_search.img_vector_db.add_video(video_path, sub_path)

    chat_search.chat_gradio(config)
