"""
sentiment_model.py

This module defines the SentimentModel class, a concrete implementation
of the OpenRouter abstract base class tailored for sentiment analysis
of Reddit posts using OpenAI models.
"""

from .openrouter_client import OpenRouter

class SentimentModel(OpenRouter):
    """
    Concrete sentiment analysis model class inheriting from OpenRouter.

    Attributes:
    - _model: OpenAI model identifier
    - _temperature: sampling temperature for generation
    - _max_tokens: max tokens to generate

    Methods:
    - _build_prompt: constructs a prompt for sentiment analysis based on post data
    """

    def __init__(self, model: str, temperature: int, max_tokens: int):
        # Initialize with specific model parameters
        super().__init__()
        self._model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        self._model = value

    @property
    def temperature(self) -> int:
        return self._temperature

    @temperature.setter
    def temperature(self, value: int) -> None:
        if not (0 <= value <= 1):
            raise ValueError("Temperature must be between 0 and 1!")
        self._temperature = value

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        if not (isinstance(value, int) and value > 0):
            raise ValueError("max_tokens must be a positive integer!")
        self._max_tokens = value

    def _build_prompt(self, **kwargs) -> str:
        # Build a detailed prompt for sentiment analysis
        title = kwargs.get("title")
        content = kwargs.get("content")
        subreddit = kwargs.get("subreddit")

        prompt = (
            "Analyze sentiment of this Reddit post using ALL available information:\n"
            f"1. Title: '{title}'\n"
            f"2. Content: '{content}'\n\n"
            f"3. Subreddit: '{subreddit}'"
            "Consider emotional tone.\n"
            "Return ONLY ONE WORD: POSITIVE, NEUTRAL, or NEGATIVE."
        )

        return prompt