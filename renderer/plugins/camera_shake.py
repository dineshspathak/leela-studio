from typing import Any

from renderer.plugins.base import BaseEffectPlugin


class CameraShakePlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        amplitude = params.get("amplitude", 5)
        # Use crop filter with coordinates shifted by sinus expressions to simulate shake
        return f"[{input_pad}]crop=w=iw-20:h=ih-20:x='10+{amplitude}*sin(2*PI*t)':y='10+{amplitude}*cos(2*PI*t)'[{output_pad}]"
