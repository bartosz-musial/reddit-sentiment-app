"""
openrouter_client.py

This module defines the OpenRouter abstract base class that manages
sentiment analysis workflow using OpenAI-compatible models and PostgreSQL storage.

It fetches unsentimented posts, builds prompts, sends requests to the model,
validates responses, and updates the database accordingly.
"""

import time
from abc import ABC, abstractmethod
from database.postgresql import PostgreSQLClient
from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionUserMessageParam
import os
import logging

class OpenRouter(ABC):
    """
    Abstract base class for OpenAI-based sentiment analysis clients.

    Attributes:
    - _storage: PostgreSQLClient instance for database operations
    - _model: model identifier string
    - _temperature: temperature setting for generation
    - _max_tokens: max tokens for model responses
    - _client: OpenAI API client instance

    Methods:
    - pipeline: process all unsentimented posts from DB
    - _build_prompt: abstract method to build prompt string (to be implemented in subclass)
    - _analyze_sentiment: send prompt and update DB with sentiment result
    - test_sentiment_model: check if the model responds correctly
    """

    def __init__(self):
        # Initialize DB client and OpenAI client
        self._storage = PostgreSQLClient()
        self._model = None
        self._temperature = None
        self._max_tokens = None
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("API_KEY")
        )

    def pipeline(self) -> None:
        # Analyze all posts without sentiment in DB
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
    def _test_prompt(**kwargs) -> str:
        # Template prompt for testing sentiment analysis
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
        # Wrap prompt in OpenAI chat message format
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "user", "content": prompt
            }
        ]

        return messages

    def _analyze_sentiment(self, post_id: str, **kwargs) -> None:
        # Analyze sentiment and update DB
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
        # Run a test sentiment query on prompt
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
        # Validate sentiment output value
        return sentiment in ("POSITIVE", "NEUTRAL", "NEGATIVE")

    def test_sentiment_model(self) -> bool:
        # Test model functionality using a known post
        post_id = self._storage.get_first_non_null_sentiment_record()
        title, content, subreddit = self._storage.get_post_to_analyze(post_id)
        prompt = self._test_prompt(title=title, content=content, subreddit=subreddit)
        try:
            self._test_analyze_sentiment(prompt)
            return True
        except OpenAIError:
            logging.warning(f"{self._model} not working properly!")
            return False