from .openrouter_client import OpenRouter

class LlamaScout(OpenRouter):
    def __init__(self):
        super().__init__()
        self._model = "meta-llama/llama-4-scout:free"
        self._temperature = 0
        self._max_tokens = 3

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