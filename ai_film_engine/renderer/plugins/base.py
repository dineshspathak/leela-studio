from abc import ABC, abstractmethod
from typing import Any


class BaseEffectPlugin(ABC):
    @abstractmethod
    def render_filter(
        self, input_pad: str, output_pad: str, params: dict[str, Any]
    ) -> str:
        """Return FFmpeg video filtergraph snippet for this effect."""
        pass
