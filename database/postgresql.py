from dotenv import load_dotenv
import datetime
import psycopg2
import os

load_dotenv()

class PostgreSQLClient:
    def __init__(self):
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
        if self._cursor and not self._cursor.closed:
            self._cursor.close()
        if self._conn and not self._conn.closed:
            self._conn.close()

    def _create_table(self) -> None:
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
        self._cursor.execute(
            "SELECT 1 FROM posts WHERE post_id = %s",
            (post_id,)
        )

        return self._cursor.fetchone() is not None

    def add_post(self, post_id: str, created_at: datetime, subreddit: str, title: str, content: str) -> None:
        self._cursor.execute(
            "INSERT INTO posts (post_id, created_at, subreddit, title, content) VALUES (%s, %s, %s, %s, %s)",
            (post_id, created_at, subreddit, title, content)
        )
        self._conn.commit()

    def update_post_sentiment(self, post_id: str, sentiment: str, model: str) -> None:
        self._cursor.execute(
            "UPDATE posts SET model_version = %s, sentiment = %s WHERE post_id = %s",
            (model, sentiment, post_id)
        )
        self._conn.commit()

    def get_unsentimented_posts(self) -> list[str]:
        self._cursor.execute(
            "SELECT post_id FROM posts WHERE sentiment IS NULL"
        )
        result = self._cursor.fetchall()

        return [row[0] for row in result]

    def get_post_to_analyze(self, post_id: str) -> tuple[str, str, str] | None:
        self._cursor.execute(
            "SELECT title, content, subreddit FROM posts WHERE post_id = %s",
            (post_id,)
        )
        result = self._cursor.fetchone()

        return result

    def get_database_size(self) -> int:
        self._cursor.execute(
            "SELECT COUNT(*) FROM posts"
        )
        result = self._cursor.fetchone()

        return result[0] if result else 0

    def update_post_sentiment_invalid(self, post_id: str, model: str) -> None:
        self._cursor.execute(
            "UPDATE posts SET model_version = %s, sentiment = %s WHERE post_id = %s",
            (model, "INVALID", post_id)
        )
        self._conn.commit()