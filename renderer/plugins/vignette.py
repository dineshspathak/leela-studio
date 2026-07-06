from typing import Any

from renderer.plugins.base import BaseEffectPlugin


class VignettePlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        angle = params.get("angle", 0.5)
        return f"[{input_pad}]vignette=angle={angle}[{output_pad}]"
