from typing import Any

from ai_film_engine.renderer.plugins.base import BaseEffectPlugin


class LetterboxPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        # Crop or pad to achieve letterbox look
        return f"[{input_pad}]drawbox=y=0:h=ih*0.1:t=fill:c=black,drawbox=y=ih-ih*0.1:h=ih*0.1:t=fill:c=black[{output_pad}]"
