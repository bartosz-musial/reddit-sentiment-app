from .openrouter_client import OpenRouter

class SentimentModel(OpenRouter):
    def __init__(self, model: str, temperature: int, max_tokens: int):
        super().__init__()
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def _build_prompt(self, **kwargs) -> str:
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