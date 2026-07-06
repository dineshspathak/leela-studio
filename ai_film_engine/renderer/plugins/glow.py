from typing import Any

from ai_film_engine.renderer.plugins.base import BaseEffectPlugin


class GlowPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        amount = params.get("amount", 1.5)
        return f"[{input_pad}]eq=brightness=0.05:saturation={amount}[{output_pad}]"
