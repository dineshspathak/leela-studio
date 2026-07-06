from typing import Any

from ai_film_engine.renderer.plugins.base import BaseEffectPlugin


class KenBurnsPlugin(BaseEffectPlugin):
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        direction = params.get("direction", "push_in")
        # Generate zoompan FFmpeg string
        if direction == "push_in":
            return f"[{input_pad}]zoompan=z='zoom+0.002':x='x':y='y':d=120:s=hd1080[{output_pad}]"
        elif direction == "push_out":
            return f"[{input_pad}]zoompan=z='2-0.002*on':x='x':y='y':d=120:s=hd1080[{output_pad}]"
        return (
            f"[{input_pad}]zoompan=z='1.1':x='x+1':y='y':d=120:s=hd1080[{output_pad}]"
        )
