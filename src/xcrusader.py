import praw
import dataset
import requests
import threading
import os
from time import sleep
from pathlib import Path

import config
import bot
from downloader import RedditDownloader, SubmissionType


class XCrusader:

    def __init__(self):
        self.reddit = praw.Reddit(
            "xcrusader", user_agent="xcrusader by u/lifeinbackground")
        self.subreddits = '+'.join(config.subreddit_names)
        self.db = dataset.connect(config.db_url)
        self.bot = bot.CrusaderBot()
        self.pending_submissions = list()
        self.downloader = RedditDownloader()

        thread = threading.Thread(
            target=self.process_pending, args=(), name='ProcessingThread')
        thread.daemon = True
        thread.start()

        self.fetch_new()

    def fetch_new(self):
        submissions = self.reddit.subreddit(
            self.subreddits).stream.submissions(skip_existing=False)
        for s in submissions:
            if self.seen(s):
                continue

            self.pending_submissions.append(s)
            print(f"[INFO] Queueing {s.shortlink}")

    def process_pending(self):
        print("[INFO] ProcessingThread started")
        while True:
            if not self.pending_submissions:
                sleep(config.process_interval)
                continue

            submissions = self.pending_submissions
            self.pending_submissions = list()

            for s in submissions:
                self.downloader.submit(s, self._downloader_callback)
            submissions.clear()

            sleep(config.process_interval)

    def seen(self,  submission):
        result = self.db['shown'].find_one(
            subreddit_name=submission.subreddit.display_name, submission_id=submission.id)
        return result != None

    def mark_as_seen(self, submission):
        self.db['shown'].insert(dict(
            chat_id=config.chat_id, subreddit_name=submission.subreddit.display_name, submission_id=submission.id))

    def _downloader_callback(self, future):
        update = future.result()
        self.bot.queue_update(update)
        self.mark_as_seen(update['submission'])


if __name__ == '__main__':
    XCrusader()
