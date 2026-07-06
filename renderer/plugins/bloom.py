from typing import Any

from renderer.plugins.base import BaseEffectPlugin


class BloomPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        radius = params.get("radius", 15)
        # Combine gblur (gaussian blur) with overlay to achieve bloom glow
        return f"[{input_pad}]split[b1][b2];[b2]gblur=sigma={radius}[blurred];[b1][blurred]blend=all_mode='addition'[{output_pad}]"
