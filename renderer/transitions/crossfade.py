from renderer.transitions.base import BaseTransitionPlugin


class CrossfadeTransition(BaseTransitionPlugin):
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        # Reconstruct standard xfade filter syntax
        return f"[{clip_a}][{clip_b}]xfade=transition=fade:duration={duration}:offset={offset}[{output_pad}]"
