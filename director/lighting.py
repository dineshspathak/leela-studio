from typing import ClassVar


class LightingEngine:
    PRESETS: ClassVar[list[str]] = [
        "golden hour",
        "moonlight",
        "torch",
        "storm",
        "volumetric",
        "soft",
        "hard",
    ]

    def recommend_lighting(self, time_of_day: str, environment: str) -> str:
        """Recommend lighting presets matching environmental profiles."""
        if time_of_day == "night":
            return "torch" if environment == "indoor" else "moonlight"
        elif time_of_day == "golden_hour":
            return "golden hour"
        elif "storm" in environment.lower() or "dungeon" in environment.lower():
            return "volumetric"
        return "soft"
