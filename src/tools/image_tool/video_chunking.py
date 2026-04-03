from pytubefix import YouTube
from pytubefix.cli import on_progress
import cv2
import whisper
import numpy as np

import json
import subprocess
from pathlib import Path
import os

class VideoChunking:
    @staticmethod
    def download_url(url:str, dir:str='./data/video') -> tuple[str, str]:
        yt = YouTube(url, on_progress_callback=on_progress)
        title = yt.title[:15].strip()
        video_dir = os.path.join(dir, title)
        os.makedirs(video_dir, exist_ok=True)

        print(f"Downloading video {title}...")
        ys = yt.streams.get_highest_resolution() # it returns the resolution of 360p anyway
        ys.download(video_dir, filename=f'{title}.mp4')
        video_path = os.path.join(video_dir, f"{title}.mp4")
        sub_path = VideoChunking._create_subtitle(video_path)

        print('~'*80)

        return video_path, sub_path

    @classmethod
    def _create_subtitle(cls, video_path:str) -> str:
        video_path:Path = Path(video_path)
        audio_path = video_path.with_suffix(".mp3")
        sub_path = video_path.with_suffix(".json")

        # if subtitle file existed, return it
        if os.path.isfile(sub_path):
            return sub_path.__str__()

        # convert mp4 to mp3
        command = f'ffmpeg -n -i "{video_path.absolute()}" -vn -ar 44100 -ac 2 -b:a 192k "{audio_path.absolute()}"'
        subprocess.call(command, shell=True)

        # convert mp3 to text
        model = whisper.load_model("base")
        subtitle = model.transcribe(audio_path.__str__())

        # write to file
        with open(sub_path, 'w') as fo:
            json.dump([{
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text']
            } for seg in subtitle['segments']], fo)

        return sub_path.__str__()

    @staticmethod
    def get_video_chunk(video_path:str, sub_path:str) -> list[dict]:
        video = cv2.VideoCapture(video_path)
        with open(sub_path, 'r') as fi:
            trans = json.load(fi)

        frame_dir = os.path.join(os.path.dirname(video_path), 'frames')
        os.makedirs(frame_dir, exist_ok=True)

        meta_data = []

        for idx, transcript in enumerate(trans):
            # get the start time and end time in seconds
            start = transcript['start'] * 1000
            end = transcript['end'] * 1000
            # print(start, end)

            for idxx, slice in enumerate(np.arange(start, end, 0.3*1000)):
                video.set(cv2.CAP_PROP_POS_MSEC, slice)
                success, frame = video.read()

                if success:
                    img_path = os.path.join(frame_dir, f'f_{idx}_{idxx}.jpeg')
                    cv2.imwrite(img_path, frame)

                    meta_data.append({
                        'frame_path': img_path,
                        'start': str(start),
                        'end': str(end),
                        'transcript': transcript['text'],
                    })

        return meta_data

if __name__=='__main__':
    video_path, sub_path = VideoChunking.download_url('https://www.youtube.com/watch?v=alDhOLhbkbY')
    print(VideoChunking.get_video_chunk(video_path, sub_path))
    # print(VideoChunking.get_video_chunk('./data/video/The Android Tab/The Android Tab.mp4', './data/video/The Android Tab/The Android Tab.json'))
