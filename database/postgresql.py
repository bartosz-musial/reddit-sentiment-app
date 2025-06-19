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
