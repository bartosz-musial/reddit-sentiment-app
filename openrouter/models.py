from .sentiment_model import SentimentModel

class LlamaScout(SentimentModel):
    def __init__(self):
        super().__init__(
            model="meta-llama/llama-4-scout:free",
            temperature=0,
            max_tokens=3
        )

class MistralNemo(SentimentModel):
    def __init__(self):
        super().__init__(
            model="mistralai/mistral-nemo:free",
            temperature=0,
            max_tokens=3
        )
