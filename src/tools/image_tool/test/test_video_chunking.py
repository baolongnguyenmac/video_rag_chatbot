from tools.video_chunking import VideoChunking

import os
from shutil import rmtree

class TestVideoChunking:
    url = 'https://www.youtube.com/watch?v=qHGTs1NSB1s'

    def test_download_url(self):
        video_path, sub_path = VideoChunking.download_url(self.url)
        print(f"Video path: {video_path}")
        print(f"Sub path: {sub_path}")

        count_video = 0
        count_sub = 0
        for file in os.listdir(os.path.dirname(video_path)):
            if file.endswith('.mp4'):
                count_video += 1
            elif file.endswith('.srt'):
                count_sub += 1

        assert count_sub == count_video

        # rmtree(os.path.dirname(video_path))

    def test_get_video_chunk(self):
        video_path, sub_path = VideoChunking.download_url(self.url)
        meta_data = VideoChunking.get_video_chunk(video_path, sub_path)

        assert len(meta_data) != 0

