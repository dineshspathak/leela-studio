from abc import ABC, abstractmethod
from pathlib import Path

from pixverse.models import VideoJob
from pixverse.schemas import ImageToVideoRequest, TextToVideoRequest


class BaseProvider(ABC):
    """Abstract Base Class for all LEELA Studio generation providers."""

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the provider."""
        pass

    @abstractmethod
    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> VideoJob:
        """Generate static image from text prompt."""
        pass

    @abstractmethod
    async def generate_image_to_video(self, request: ImageToVideoRequest) -> VideoJob:
        """Generate video using an image reference and optional text prompt."""
        pass

    @abstractmethod
    async def generate_text_to_video(self, request: TextToVideoRequest) -> VideoJob:
        """Generate video from text prompt."""
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> VideoJob:
        """Retrieve status of submitted task."""
        pass

    @abstractmethod
    async def download_asset(
        self,
        url: str,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        job: VideoJob,
        elapsed_time: float,
        references: list[str] | None = None,
    ) -> Path:
        """Download asset to local path."""
        pass

    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel task."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider's health status."""
        pass
