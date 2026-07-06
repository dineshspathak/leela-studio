from typing import Any

from ai_film_engine.renderer.plugins.base import BaseEffectPlugin


class RainPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        # Mock rain using line overlays or drawgrid
        return f"[{input_pad}]drawgrid=w=2:h=20:t=1:c=blue@0.2[{output_pad}]"
