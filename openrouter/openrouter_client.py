import time
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from database.postgresql import PostgreSQLClient
from openai import OpenAI, AuthenticationError
from openai.types.chat import ChatCompletionUserMessageParam
import os
import logging

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

    def pipeline(self):
        posts_id = self._storage.get_unsentimented_posts()
        logging.info(f"Posts to analyze: {len(posts_id)}")
        for num, post_id in enumerate(posts_id):
            title, content, subreddit = self._storage.get_post_to_analyze(post_id)
            logging.info(f"Analyzing sentiment for: {post_id} using {self._model}")
            self._analyze_sentiment(post_id, title=title, content=content, subreddit=subreddit)
            logging.info(f"Queue: {len(posts_id) - num}")
            time.sleep(5)
        logging.info(f"Sentiment analysis DONE")

    @abstractmethod
    def _build_prompt(self, **kwargs) -> str:
        """
        Generates a prompt appropriate to the task at hand (e.g., sentiment analysis, summary, etc.).
        """
        pass

    @staticmethod
    def _test_prompt(**kwargs):
        title = kwargs.get("title")
        content = kwargs.get("content")
        subreddit = kwargs.get("subreddit")

        prompt = (
            "Determine the sentiment of this Reddit post:"
            f"1. Title: '{title}'"
            f"2. Content: '{content}'"
            f"3. Subreddit: '{subreddit}'"
            "Respond with ONE WORD: POSITIVE, NEUTRAL, or NEGATIVE."
        )

        return prompt

    @staticmethod
    def _messages(prompt: str) -> list[ChatCompletionUserMessageParam]:
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "user", "content": prompt
            }
        ]

        return messages

    def _analyze_sentiment(self, post_id: str, **kwargs):
        prompt = self._build_prompt(**kwargs)
        messages = self._messages(prompt)

        chat = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens
        )
        sentiment = chat.choices[0].message.content.strip().upper()
        if self._sentiment_validation(sentiment):
            self._storage.update_post_sentiment(post_id, sentiment, self._model)
        else:
            logging.warning(f"Invalid sentiment value returned: {sentiment}")
            self._storage.update_post_sentiment_invalid(post_id, self._model)

    def _test_analyze_sentiment(self, prompt: str) -> str:
        messages = self._messages(prompt)

        chat = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens
        )
        sentiment = chat.choices[0].message.content.strip().upper()

        return sentiment

    @staticmethod
    def _sentiment_validation(sentiment: str) -> bool:
        return sentiment in ("POSITIVE", "NEUTRAL", "NEGATIVE")

    def test_sentiment_model(self) -> bool:
        post_id = self._storage.get_first_non_null_sentiment_record()
        title, content, subreddit = self._storage.get_post_to_analyze(post_id)
        prompt = self._test_prompt(title=title, content=content, subreddit=subreddit)
        try:
            self._test_analyze_sentiment(prompt)
            return True
        except AuthenticationError:
            logging.warning(f"{self._model} not working properly!")
            return False