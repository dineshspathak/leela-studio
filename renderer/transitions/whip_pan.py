from renderer.transitions.base import BaseTransitionPlugin


class WhipPanTransition(BaseTransitionPlugin):
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        # Standard slide or wipe transition to mimic a whip pan sweep
        return f"[{clip_a}][{clip_b}]xfade=transition=slidedown:duration={duration}:offset={offset}[{output_pad}]"
