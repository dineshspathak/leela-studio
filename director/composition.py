from typing import ClassVar


class CompositionEngine:
    COMPOSITIONS: ClassVar[list[str]] = [
        "rule of thirds",
        "center",
        "leading lines",
        "symmetry",
        "silhouette",
    ]

    def recommend_composition(self, framing: str, is_character: bool = True) -> str:
        """Recommend aesthetic composition rule."""
        mapping = {
            "close up": "center",
            "wide": "rule of thirds",
            "low angle": "silhouette",
        }
        return mapping.get(framing, "rule of thirds")
