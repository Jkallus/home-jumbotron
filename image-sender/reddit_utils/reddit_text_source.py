
import os
from dotenv import load_dotenv
import praw
from reddit_utils.text_source import TextSource

load_dotenv()

class RedditTextSource(TextSource):
    def __init__(self) -> None:
        super().__init__()
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        self.reddit = praw.Reddit(
            client_id = self.client_id,
            client_secret = self.client_secret,
            user_agent = self.user_agent
        )
        