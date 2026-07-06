from typing import Any

from ai_film_engine.renderer.plugins.base import BaseEffectPlugin


class DustPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        amount = params.get("amount", 2)
        # Mock dust using random scatter points via noise or grids
        return f"[{input_pad}]noise=alls={amount}:allf=t+u[{output_pad}]"
