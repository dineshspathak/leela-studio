from ai_film_engine.renderer.transitions.base import BaseTransitionPlugin


class ZoomTransition(BaseTransitionPlugin):
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        return f"[{clip_a}][{clip_b}]xfade=transition=zoomin:duration={duration}:offset={offset}[{output_pad}]"
