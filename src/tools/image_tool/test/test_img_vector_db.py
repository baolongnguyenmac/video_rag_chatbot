from tools.img_vector_db import ImageVectorDB
from tools.video_chunking import VideoChunking

import os
from shutil import rmtree

class TestImageVectorDB:
    persist_directory='./src/tools/test/img_db'
    collection_name='test_img'
    vector_db = ImageVectorDB(
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    url = 'https://www.youtube.com/watch?v=qHGTs1NSB1s' # Why Linus Torvalds doesn't use Ubuntu or Debian
    video_path, sub_path = VideoChunking.download_url(url)

    search_by_text = vector_db.search_img_by_text(k=3)
    search_by_img = vector_db.search_img_by_img(k=3)

    def test_add_video(self):
        self.vector_db.add_video(self.video_path, self.sub_path)

    def test_search_by_text(self):
        str_ = self.search_by_text.invoke('a man with microphone')
        assert str_ is not None
        assert str_ != ''

    def test_search_by_img(self):
        dir = os.path.dirname(self.video_path)
        frame_dir = os.path.join(dir, 'frames')
        filename = os.listdir(frame_dir)[0]
        str_ = self.search_by_img.invoke(os.path.join(frame_dir, filename))
        assert str_ is not None
        assert str_ != ''

    def test_remove_collection(self):
        rmtree(self.persist_directory)
