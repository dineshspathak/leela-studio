from typing import ClassVar


class EmotionsEngine:
    EMOTIONS: ClassVar[list[str]] = [
        "fear",
        "hope",
        "sadness",
        "divine",
        "anger",
        "joy",
        "devotion",
    ]

    def recommend_emotion(self, prompt: str) -> str:
        """Map dialogue/action context to target emotional resonance."""
        low_prompt = prompt.lower()
        if "crying" in low_prompt or "weep" in low_prompt or "sorrow" in low_prompt:
            return "sadness"
        elif "fear" in low_prompt or "scared" in low_prompt or "kamsa" in low_prompt:
            return "fear"
        elif (
            "prayer" in low_prompt or "worship" in low_prompt or "divine" in low_prompt
        ):
            return "devotion"
        elif "smile" in low_prompt or "laugh" in low_prompt:
            return "joy"
        return "hope"
