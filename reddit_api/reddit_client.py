from praw import Reddit
from dotenv import load_dotenv
from database.postgresql import PostgreSQLClient
from datetime import datetime, timezone
import os
import logging
import logging_config
import time

logging_config.get_config()

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
                created_at = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                self._database.add_post(
                    submission.id,
                    created_at,
                    subreddit,
                    submission.title,
                    submission.selftext
                )
                logging.info(f"Added post {submission.id} from r/{subreddit}")
                time.sleep(1)
            logging.info("No more posts to fetch")
            logging.info(f"Database size: {self._database.get_database_size()}")