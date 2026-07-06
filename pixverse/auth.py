class PixVerseAuth:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("PixVerse API Key must not be empty.")
        self.api_key = api_key

    def get_headers(self, trace_id: str) -> dict[str, str]:
        return {
            "API-KEY": self.api_key,
            "Ai-trace-id": trace_id,
            "Content-Type": "application/json",
        }
