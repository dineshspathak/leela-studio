from pathlib import Path

from pixverse.client import PixVerseClient
from pixverse.downloads import PixVerseDownloads
from pixverse.jobs import PixVerseJobs
from pixverse.models import VideoJob
from pixverse.schemas import ImageToVideoRequest, TextToVideoRequest
from providers.base import BaseProvider


class PixVerseProvider(BaseProvider):
    def __init__(self, client: PixVerseClient):
        self.client = client
        self.jobs = PixVerseJobs(client)
        self.downloads = PixVerseDownloads(client.http_client)

    async def authenticate(self) -> bool:
        """Validate API key presence."""
        return bool(self.client.api_key)

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> VideoJob:
        """Generate a static image using PixVerse client."""
        return await self.jobs.generate_image(prompt, aspect_ratio)

    async def generate_image_to_video(self, request: ImageToVideoRequest) -> VideoJob:
        """Submit image-to-video request using PixVerse client."""
        return await self.jobs.generate_image_to_video(request)

    async def generate_text_to_video(self, request: TextToVideoRequest) -> VideoJob:
        """Submit text-to-video request using PixVerse client."""
        return await self.jobs.generate_text_to_video(request)

    async def get_task_status(self, task_id: str) -> VideoJob:
        """Get status from PixVerse client."""
        return await self.jobs.get_task_status(task_id)

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
        """Download asset to structured local path."""
        return await self.downloads.download_asset(
            url=url,
            episode_id=episode_id,
            scene_id=scene_id,
            shot_id=shot_id,
            job=job,
            elapsed_time=elapsed_time,
            references=references,
        )

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel task using PixVerse client."""
        return await self.jobs.cancel_task(task_id)

    async def health_check(self) -> bool:
        """Perform API health check."""
        return await self.jobs.health_check()
