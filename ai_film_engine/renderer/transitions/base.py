from abc import ABC, abstractmethod


class BaseTransitionPlugin(ABC):
    @abstractmethod
    def render_transition(
        self, clip_a: str, clip_b: str, output_pad: str, offset: float, duration: float
    ) -> str:
        """Return FFmpeg filtergraph snippet combining two inputs with this transition."""
        pass
