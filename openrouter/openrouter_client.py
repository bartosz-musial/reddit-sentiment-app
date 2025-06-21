from abc import ABC, abstractmethod
from dotenv import load_dotenv
from database.postgresql import PostgreSQLClient
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
import os

load_dotenv()

class OpenRouter(ABC):
    def __init__(self):
        self._storage = PostgreSQLClient()
        self.model = None
        self.temperature = None
        self.max_tokens = None
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("API_KEY")
        )
