import requests
import youtube_dl
import concurrent.futures
from pathlib import Path
from enum import Enum

import config


class SubmissionType(Enum):
    PHOTO = 0
    VIDEO = 1


class RedditDownloader:

    def __init__(self):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo',
            'outtmpl': str(config.download_dir / '%(id)s.%(ext)s'),
            'noplaylist': True,
            'forceduration': True,
            'quiet': True,
        }
        print('outtmpl: ' + ydl_opts['outtmpl'])
        self.ydl = youtube_dl.YoutubeDL(ydl_opts)
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=config.downloader_max_workers)

    def submit(self, s, callback):
        future = None
        if s.url.endswith(config.image_exts):
            future = self.executor.submit(self.download_photo, s.url, s)
        elif s.media is not None:
            if 'reddit_video' in s.media and 'fallback_url' in s.media['reddit_video']:
                url = s.media['reddit_video']['fallback_url']
                future = self.executor.submit(self.download_video, url, s)
            elif 'type' in s.media and s.media['type'] == 'youtube.com':
                future = self.executor.submit(self.download_video, s.url, s)
        else:
            print(f'[WARNING] Unsupported submission type: {s.shortlink}')

        if future is not None:
            future.add_done_callback(callback)

    def download_photo(self, url, submission):
        print(f"Downloading photo {url} ({submission.shortlink})")
        file_name = url.split('/')[-1]
        response = requests.get(url)

        if not response.status_code == requests.codes.ok:
            print(f"[WARNING] The response for {url} is not OK")
            return

        file_path = config.download_dir / file_name
        with open(file_path, 'wb+') as f:
            f.write(response.content)

        return {'type': SubmissionType.PHOTO, 'file_path': file_path, 'submission': submission}

    def download_video(self, url, submission):
        print(f"Downloading video {url} ({submission.shortlink})")
        filename = None
        try:
            info = self.ydl.extract_info(url)
            filename = self.ydl.prepare_filename(info)
        except Exception as e:
            print(e)

        file_path = Path(filename)
        return {'type': SubmissionType.VIDEO, 'file_path': file_path, 'submission': submission}
