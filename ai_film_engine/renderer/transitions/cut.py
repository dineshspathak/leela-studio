from ai_film_engine.renderer.transitions.base import BaseTransitionPlugin


class CutTransition(BaseTransitionPlugin):
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        # A simple cut concatenates both clips directly.
        return f"[{clip_a}][{clip_b}]concat=n=2:v=1:a=0[{output_pad}]"
