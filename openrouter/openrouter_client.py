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
        self._model = None
        self._temperature = None
        self._max_tokens = None
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("API_KEY")
        )

    @abstractmethod
    def _build_prompt(self, **kwargs) -> str:
        """
        Generates a prompt appropriate to the task at hand (e.g., sentiment analysis, summary, etc.).
        """
        pass

    def _analyze_sentiment(self, **kwargs):
        prompt = self._build_prompt(**kwargs)
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "user", "content": prompt
            }
        ]

        chat = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens
        )
        sentiment = chat.choices[0].message.content.strip()

    @staticmethod
    def _sentiment_validation(sentiment: str) -> bool:
        return sentiment.upper() in ("POSITIVE", "NEUTRAL", "NEGATIVE")