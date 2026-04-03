from tools.text_chunking import TextChunking
from langchain_core.documents.base import Document
from pytubefix import YouTube
from pytubefix.cli import on_progress

import os

class TestTextChunking:
    test_dir = './src/extractor/test'

    def test_get_pdf_chunk(self):
        pdf_url = 'https://arxiv.org/pdf/1912.04977'
        filepath = os.path.join(self.test_dir, 'test.pdf')
        os.system(f'curl -sSL -o {filepath} {pdf_url}')

        docs = TextChunking.get_pdf_chunk(filepath)

        assert type(docs) is list
        assert type(docs[0]) is Document

        os.remove(filepath)

    def test_get_srt_chunk(self):
        # get data
        video_url = 'https://www.youtube.com/watch?v=qHGTs1NSB1s'
        yt = YouTube(video_url, on_progress_callback=on_progress)
        caption = yt.captions[yt.caption_tracks[0].code]
        filepath = os.path.join(self.test_dir, 'test.srt')
        caption.save_captions(filepath)

        docs = TextChunking.get_srt_chunk(filepath)
        for doc in docs[:3]:
            print(doc.page_content)
            print('~'*80)

        assert type(docs) is list
        assert type(docs[0]) is Document

        os.remove(filepath)

if __name__=='__main__':
    tester = TestTextChunking()
    tester.test_get_srt_chunk()
