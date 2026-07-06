from typing import ClassVar


class CameraEngine:
    FRAMINGS: ClassVar[list[str]] = [
        "close up",
        "medium",
        "wide",
        "over shoulder",
        "bird eye",
        "low angle",
        "high angle",
    ]
    MOVEMENTS: ClassVar[list[str]] = [
        "push in",
        "push out",
        "pan left",
        "pan right",
        "crane",
        "handheld",
        "locked",
        "dolly",
    ]

    def recommend_setup(self, importance: str, is_action: bool = False) -> dict:
        """Decide camera parameters based on shot settings."""
        if importance == "HERO":
            framing = "low angle" if is_action else "close up"
            movement = "handheld" if is_action else "push in"
        elif importance == "IMPORTANT":
            framing = "medium"
            movement = "dolly"
        elif importance == "BACKGROUND":
            framing = "wide"
            movement = "locked"
        else:
            framing = "medium"
            movement = "locked"

        return {
            "framing": framing,
            "movement": movement,
        }
