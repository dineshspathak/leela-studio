from typing import ClassVar


class MotionEngine:
    MOTIONS: ClassVar[list[str]] = [
        "cloth",
        "hair",
        "rain",
        "light",
        "particles",
        "breathing",
        "eyes",
        "hands",
    ]

    def recommend_motion(self, framing: str, is_storm: bool = False) -> str:
        """Recommend primary visual motion details to emphasize."""
        if is_storm:
            return "rain and atmospheric particles"
        if framing == "close up":
            return "breathing and micro eyes movement"
        return "cloth and hair floating simulation"
