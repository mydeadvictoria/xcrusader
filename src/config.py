import os
from pathlib import Path

subreddit_names = ("Animemes", "ShitPostCrusaders")
db_url = 'sqlite:///seen.db'
download_dir = Path('Downloads/')
chat_id = '@pixiepy'
image_exts = ('.jpg', '.jpeg', '.png', '.gif')
# max_video_duration = 500
process_interval = 5
bot_process_updates_interval = 10
bot_max_num_of_retries = 2
bot_delay_before_retry = 10
bot_token = os.environ.get('BOT_TOKEN')
new_posts_limit = 15
downloader_max_workers = 5

if not bot_token:
    print('BOT_TOKEN is not set')

if not download_dir.exists():
    download_dir.mkdir(parents=True, exist_ok=True)
