from ai_film_engine.renderer.transitions.base import BaseTransitionPlugin


class BlurTransition(BaseTransitionPlugin):
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        # Crossfade using radial blur/crosswarp style transitions
        return f"[{clip_a}][{clip_b}]xfade=transition=radialblur:duration={duration}:offset={offset}[{output_pad}]"
