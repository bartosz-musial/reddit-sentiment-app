"""
reddit_client.py

This module contains the RedditClient class responsible for fetching new posts
from specified subreddits using the PRAW library and storing them in a PostgreSQL database.
"""

from praw import Reddit
from backend.database.postgresql import PostgreSQLClient
from datetime import datetime, timezone
import os
import logging
import time

class RedditClient:
    """
    RedditClient handles interaction with Reddit API to retrieve new posts
    and store them in a database.

    Methods:
    - from_env: initializes Reddit client using environment variables
    - get_new_posts: fetches new posts from a subreddit and saves those not already in the database
    """

    def __init__(self, reddit_client: Reddit):
        # Initialize with an existing PRAW Reddit client and PostgreSQL client
        self._reddit = reddit_client
        self._database = PostgreSQLClient()

    @classmethod
    def from_env(cls):
        # Create Reddit client using environment variables
        client = Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT")
        )

        return cls(client)

    def get_new_posts(self, subreddit: str, limit: int) -> None:
        """
        Fetches new posts from a subreddit up to a specified limit.
        Adds only posts that don't already exist in the database.
        """
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