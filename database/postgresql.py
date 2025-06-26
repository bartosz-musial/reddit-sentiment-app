"""
postgresql.py

This module contains the PostgreSQLClient class responsible for managing
connections and operations with a PostgreSQL database for storing Reddit posts
and their sentiment analysis results.

The class provides methods to create the necessary table, insert new posts,
check existence, update sentiment information, and query posts for analysis.
"""

import datetime
import psycopg2
import os

class PostgreSQLClient:
    """
    PostgreSQLClient handles the connection to the PostgreSQL database
    and provides methods to manage Reddit posts and their sentiment data.

    Key methods:
    - __init__: Initializes the connection and creates the posts table if it does not exist.
    - close: Closes the cursor and connection.
    - post_exists: Checks if a post with a given post_id exists in the database.
    - add_post: Inserts a new post record into the database.
    - update_post_sentiment: Updates the sentiment and model version of a post.
    - get_unsentimented_posts: Retrieves all post_ids that have no sentiment assigned yet.
    - get_post_to_analyze: Retrieves the title, content, and subreddit of a post by post_id.
    - get_database_size: Returns the total number of posts stored.
    - update_post_sentiment_invalid: Marks a post's sentiment as INVALID.
    - get_first_non_null_sentiment_record: Gets the post_id of the first post with a non-null sentiment.
    """

    def __init__(self):
        # Initialize connection and cursor, create posts table if needed
        self._conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        self._cursor = self._conn.cursor()
        self._create_table()

    def close(self) -> None:
        # Safely close the database cursor and connection
        if self._cursor and not self._cursor.closed:
            self._cursor.close()
        if self._conn and not self._conn.closed:
            self._conn.close()

    def _create_table(self) -> None:
        # Create the 'posts' table if it does not already exist
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                post_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                subreddit TEXT,
                title TEXT,
                content TEXT,
                sentiment TEXT,
                model_version TEXT
            );
        ''')
        self._conn.commit()

    def post_exists(self, post_id: str) -> bool:
        # Check if a post with the given post_id exists in the database
        self._cursor.execute(
            "SELECT 1 FROM posts WHERE post_id = %s",
            (post_id,)
        )

        return self._cursor.fetchone() is not None

    def add_post(self, post_id: str, created_at: datetime, subreddit: str, title: str, content: str) -> None:
        # Insert a new post into the database
        self._cursor.execute(
            "INSERT INTO posts (post_id, created_at, subreddit, title, content) VALUES (%s, %s, %s, %s, %s)",
            (post_id, created_at, subreddit, title, content)
        )
        self._conn.commit()

    def update_post_sentiment(self, post_id: str, sentiment: str, model: str) -> None:
        # Update sentiment and model version for a given post
        self._cursor.execute(
            "UPDATE posts SET model_version = %s, sentiment = %s WHERE post_id = %s",
            (model, sentiment, post_id)
        )
        self._conn.commit()

    def get_unsentimented_posts(self) -> list[str]:
        # Retrieve all post_ids where sentiment is not yet assigned
        self._cursor.execute(
            "SELECT post_id FROM posts WHERE sentiment IS NULL"
        )
        result = self._cursor.fetchall()

        return [row[0] for row in result]

    def get_post_to_analyze(self, post_id: str) -> tuple[str, str, str] | None:
        # Get title, content, and subreddit for a post by post_id
        self._cursor.execute(
            "SELECT title, content, subreddit FROM posts WHERE post_id = %s",
            (post_id,)
        )
        result = self._cursor.fetchone()

        return result

    def get_database_size(self) -> int:
        # Return the total number of posts in the database
        self._cursor.execute(
            "SELECT COUNT(*) FROM posts"
        )
        result = self._cursor.fetchone()

        return result[0] if result else 0

    def update_post_sentiment_invalid(self, post_id: str, model: str) -> None:
        # Mark a post's sentiment as INVALID with specified model version
        self._cursor.execute(
            "UPDATE posts SET model_version = %s, sentiment = %s WHERE post_id = %s",
            (model, "INVALID", post_id)
        )
        self._conn.commit()

    def get_first_record(self) -> str | None:
        # Retrieve post_id of the first post that has a non-null sentiment value
        self._cursor.execute(
            "SELECT post_id FROM posts LIMIT 1"
        )
        result = self._cursor.fetchone()
        if result is None:
            return None

        return result[0]