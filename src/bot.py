import telegram
import config
import threading
from time import sleep
from telegram.utils.helpers import escape_markdown
from downloader import SubmissionType


class CrusaderBot:

    def __init__(self):
        self.bot = telegram.Bot(token=config.bot_token)
        print(f"[INFO] Bot username: {self.bot.get_me()['username']}")
        self.pending_updates = list()
        thread = threading.Thread(
            target=self.process_updates, args=(), name='BotThread')
        thread.daemon = True
        thread.start()

    def queue_update(self, update):
        self.pending_updates.append(update)

    def process_updates(self):
        print("[INFO] BotThread started")
        while True:
            if not self.pending_updates:
                print(
                    f'[INFO] No pending updates. Sleeping for {config.bot_process_updates_interval}...')
                sleep(config.bot_process_updates_interval)
                continue

            print('[INFO] Processing updates...')

            pending_updates = self.pending_updates
            self.pending_updates = list()

            for u in pending_updates:
                caption = self.generate_caption(u['submission'])
                file_path = u['file_path']
                s_type = u['type']
                num_of_retries = 0
                print(f"Uploading {file_path}")
                while True:
                    try:
                        if s_type == SubmissionType.PHOTO:
                            self.send_photo(file_path, caption)
                        elif s_type == SubmissionType.VIDEO:
                            self.send_video(file_path, caption)
                    except telegram.TelegramError as e:
                        print('TelegramError: ' + str(e))
                        num_of_retries += 1
                        if num_of_retries > config.bot_max_num_of_retries:
                            print(
                                f'Max number of retries[{config.bot_max_num_of_retries}] reached. Skipping...')
                            break
                        print(
                            f'Retrying in {config.bot_delay_before_retry}...')
                        sleep(config.bot_delay_before_retry)
                        continue
                    break

                file_path.unlink(missing_ok=True)

            sleep(config.bot_process_updates_interval)

    def send_photo(self, photo_path, caption):
        self.bot.send_photo(chat_id=config.chat_id, photo=open(
            photo_path, 'rb'), caption=caption, parse_mode=telegram.ParseMode.MARKDOWN)

    def send_video(self, video_path, caption):
        self.bot.send_video(chat_id=config.chat_id, video=open(
            video_path, 'rb'), caption=caption, parse_mode=telegram.ParseMode.MARKDOWN)

    def generate_caption(self, s):
        subreddit = f"r/{escape_markdown(s.subreddit.display_name)}"
        user = f"u/{escape_markdown(s.author.name)}"
        return f"Posted on {subreddit} by {user} \[[redd.it]({s.shortlink})]"
