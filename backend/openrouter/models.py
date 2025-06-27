"""
models.py

This module defines specific sentiment analysis model classes
that inherit from the base SentimentModel.

Classes:
- LlamaScout: Uses the "meta-llama/llama-4-scout" model with fixed parameters.
- MistralNemo: Uses the "mistralai/mistral-nemo" model with fixed parameters.
"""

from .sentiment_model import SentimentModel

class LlamaScout(SentimentModel):
    """
    SentimentModel subclass using the meta-llama/llama-4-scout model.
    """

    def __init__(self):
        super().__init__(
            model="meta-llama/llama-4-scout:free",
            temperature=0,
            max_tokens=3
        )

class MistralNemo(SentimentModel):
    """
    SentimentModel subclass using the mistralai/mistral-nemo model.
    """

    def __init__(self):
        super().__init__(
            model="mistralai/mistral-nemo:free",
            temperature=0,
            max_tokens=3
        )
