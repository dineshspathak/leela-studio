import json
import time
from pathlib import Path

import httpx

from ai_film_engine.core.config.logging import logger
from ai_film_engine.providers.pixverse.models import VideoJob


class PixVerseDownloads:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.http_client = http_client or httpx.AsyncClient()

    async def download_asset(
        self,
        url: str,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        job: VideoJob,
        elapsed_time: float,
        references: list[str] | None = None,
        base_dir: str = "downloads",
    ) -> Path:
        """Download video/image from URL and save with metadata asset.json alongside."""
        # Standardize directories
        episode_dir = (
            f"Episode{episode_id.zfill(3)}" if episode_id.isdigit() else episode_id
        )
        scene_dir = f"Scene{scene_id.zfill(3)}" if scene_id.isdigit() else scene_id

        target_dir = Path(base_dir) / episode_dir / scene_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        # Resolve file extension from URL or fallback to mp4
        ext = ".mp4"
        if ".png" in url.lower() or ".jpg" in url.lower() or ".jpeg" in url.lower():
            ext = ".png"

        file_name = (
            f"Shot{shot_id.zfill(3)}{ext}" if shot_id.isdigit() else f"{shot_id}{ext}"
        )
        dest_path = target_dir / file_name

        logger.info("Starting asset download", url=url, destination=str(dest_path))

        # Stream download chunks
        async with self.http_client.stream("GET", url) as response:
            response.raise_for_status()
            # Open file in write-binary mode
            with open(dest_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

        try:
            local_path = str(dest_path.resolve().relative_to(Path(".").resolve()))
        except ValueError:
            local_path = str(dest_path.resolve())

        # Generate metadata
        metadata = {
            "job_id": job.video_id,
            "prompt": job.prompt,
            "references": references or [],
            "provider": "ai_film_engine.providers.pixverse",
            "generation_time": elapsed_time,
            "seed": job.seed,
            "duration": job.duration,
            "resolution": job.resolution,
            "created_at": job.created_at
            or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "local_path": local_path,
        }

        metadata_path = dest_path.with_name(f"{dest_path.stem}_asset.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(
            "Asset download complete",
            local_path=str(dest_path),
            metadata_path=str(metadata_path),
        )
        return dest_path
