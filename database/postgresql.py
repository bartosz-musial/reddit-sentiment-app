from dotenv import load_dotenv
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
                subreddit TEXT,
                title TEXT,
                content TEXT,
                sentiment TEXT,
                model_version TEXT,
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self._conn.commit()

    def post_exists(self, post_id: str) -> bool:
        self._cursor.execute(
            "SELECT 1 FROM posts WHERE post_id = %s",
            (post_id,)
        )

        return self._cursor.fetchone() is not None

    def add_post(self, post_id: str, subreddit: str, title: str, content: str) -> None:
        self._cursor.execute(
            "INSERT INTO posts (post_id, subreddit, title, content) VALUES (%s, %s, %s, %s)",
            (post_id, subreddit, title, content)
        )
        self._conn.commit()
