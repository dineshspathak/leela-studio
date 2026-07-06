from typing import Any

from ai_film_engine.renderer.plugins.base import BaseEffectPlugin


class GrainPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        intensity = params.get("intensity", 5)
        return f"[{input_pad}]noise=alls={intensity}:allf=t+u[{output_pad}]"
