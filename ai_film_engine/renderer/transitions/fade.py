from ai_film_engine.renderer.transitions.base import BaseTransitionPlugin


class FadeTransition(BaseTransitionPlugin):
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        return f"[{clip_a}]fade=t=out:st={offset}:d={duration}[faded_a];[faded_a][{clip_b}]concat=n=2:v=1:a=0[{output_pad}]"
