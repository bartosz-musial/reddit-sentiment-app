from praw import Reddit
from dotenv import load_dotenv
from database.postgresql import PostgreSQLClient
import os

load_dotenv()

class RedditClient:
    def __init__(self, reddit_client: Reddit):
        self._reddit = reddit_client
        self._database = PostgreSQLClient()

    @classmethod
    def from_env(cls):
        client = Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT")
        )

        return cls(client)

    def get_new_posts(self, subreddit: str, limit: int) -> None:
        for submission in self._reddit.subreddit(subreddit).new(limit=limit):
            if not self._database.post_exists(submission.id):
                self._database.add_post(
                    submission.id,
                    subreddit,
                    submission.title,
                    submission.selftext
                )
