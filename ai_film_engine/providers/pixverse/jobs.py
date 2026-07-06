import asyncio
import json
import time
from pathlib import Path
from typing import Any

from ai_film_engine.core.config.logging import logger
from ai_film_engine.providers.pixverse.client import PixVerseClient
from ai_film_engine.providers.pixverse.downloads import PixVerseDownloads
from ai_film_engine.providers.pixverse.models import JobStatus, VideoJob
from ai_film_engine.providers.pixverse.schemas import (
    ImageToVideoRequest,
    PixVerseEnvelope,
    TextToVideoRequest,
)


class PixVerseJobs:
    def __init__(self, client: PixVerseClient):
        self.client = client

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> VideoJob:
        """Submit text-to-image request."""
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "mode": "image",
        }
        res = await self.client._request("POST", "/image/generate", json_data=payload)
        envelope = PixVerseEnvelope(**res)
        if not envelope.data or not envelope.data.video_id:
            raise ValueError(f"Invalid API response: {res}")
        return VideoJob(
            video_id=envelope.data.video_id,
            status=JobStatus.GENERATING,
            prompt=prompt,
        )

    async def generate_text_to_video(
        self,
        request: TextToVideoRequest,
    ) -> VideoJob:
        """Submit text-to-video request."""
        res = await self.client._request(
            "POST",
            "/video/text/generate",
            json_data=request.model_dump(exclude_none=True),
        )
        envelope = PixVerseEnvelope(**res)
        if not envelope.data or not envelope.data.video_id:
            raise ValueError(f"Invalid API response: {res}")
        return VideoJob(
            video_id=envelope.data.video_id,
            status=JobStatus.GENERATING,
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.quality,
        )

    async def generate_image_to_video(
        self,
        request: ImageToVideoRequest,
    ) -> VideoJob:
        """Submit image-to-video request."""
        res = await self.client._request(
            "POST",
            "/video/img/generate",
            json_data=request.model_dump(exclude_none=True),
        )
        envelope = PixVerseEnvelope(**res)
        if not envelope.data or not envelope.data.video_id:
            raise ValueError(f"Invalid API response: {res}")
        return VideoJob(
            video_id=envelope.data.video_id,
            status=JobStatus.GENERATING,
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.quality,
        )

    async def get_task_status(self, video_id: str) -> VideoJob:
        """Get status of a video/image generation task."""
        res = await self.client._request("GET", f"/video/result/{video_id}")
        envelope = PixVerseEnvelope(**res)
        if not envelope.data:
            raise ValueError(f"Invalid API response: {res}")

        status_val = envelope.data.status
        try:
            status = (
                JobStatus(status_val)
                if status_val is not None
                else JobStatus.GENERATING
            )
        except ValueError:
            status = JobStatus.FAILED

        return VideoJob(
            video_id=envelope.data.video_id,
            status=status,
            prompt=envelope.data.video_url or "",
            video_url=envelope.data.video_url,
            seed=envelope.data.seed,
            duration=envelope.data.duration,
            resolution=envelope.data.resolution,
            created_at=envelope.data.created_at,
        )

    async def cancel_task(self, video_id: str) -> bool:
        """Cancel a video/image generation task."""
        payload = {"video_id": video_id}
        res = await self.client._request("POST", "/video/cancel", json_data=payload)
        envelope = PixVerseEnvelope(**res)
        return envelope.code == 0

    async def health_check(self) -> bool:
        """Validate connectivity and authentication."""
        try:
            res = await self.client._request("GET", "/account/balance")
            envelope = PixVerseEnvelope(**res)
            return envelope.code == 0
        except Exception:
            return False


class JobManager:
    def __init__(
        self,
        jobs_api: PixVerseJobs,
        downloads_api: PixVerseDownloads,
        active_jobs_file: str = "cache/active_jobs.json",
        max_parallel_jobs: int = 2,
    ):
        self.jobs_api = jobs_api
        self.downloads_api = downloads_api
        self.active_jobs_file = Path(active_jobs_file)
        self.max_parallel_jobs = max_parallel_jobs
        self.active_jobs: dict[str, dict[str, Any]] = {}

        # Load any pending checkpoint jobs on startup
        self.load_jobs()

    def persist_jobs(self):
        """Save currently running jobs list to a json file for checkpoint recovery."""
        self.active_jobs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.active_jobs_file, "w", encoding="utf-8") as f:
            json.dump(self.active_jobs, f, indent=2)
        logger.info("Persisted active jobs checkpoint", count=len(self.active_jobs))

    def load_jobs(self):
        """Load running jobs list from json file on startup."""
        if self.active_jobs_file.exists():
            try:
                with open(self.active_jobs_file, encoding="utf-8") as f:
                    self.active_jobs = json.load(f)
                logger.info(
                    "Loaded active jobs checkpoint", count=len(self.active_jobs)
                )
            except Exception as e:
                logger.error("Failed to load checkpoint file", error=str(e))
                self.active_jobs = {}

    async def submit_text_to_video(
        self,
        request: TextToVideoRequest,
        episode_id: str,
        scene_id: str,
        shot_id: str,
    ) -> VideoJob:
        """Submit text-to-video job, register for tracking/checkpoint,
        and return job info.
        """
        job = await self.jobs_api.generate_text_to_video(request)
        self.active_jobs[job.video_id] = {
            "video_id": job.video_id,
            "prompt": request.prompt,
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "submitted_at": time.time(),
            "references": [],
        }
        self.persist_jobs()
        return job

    async def submit_image_to_video(
        self,
        request: ImageToVideoRequest,
        episode_id: str,
        scene_id: str,
        shot_id: str,
    ) -> VideoJob:
        """Submit image-to-video job, register for tracking/checkpoint,
        and return job info.
        """
        job = await self.jobs_api.generate_image_to_video(request)
        self.active_jobs[job.video_id] = {
            "video_id": job.video_id,
            "prompt": request.prompt,
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "submitted_at": time.time(),
            "references": [request.image_url],
        }
        self.persist_jobs()
        return job

    async def poll_and_download(
        self,
        video_id: str,
        polling_interval: float = 5.0,
    ) -> Path:
        """Poll a job until success/failure and download the completed asset."""
        if video_id not in self.active_jobs:
            raise KeyError(f"Job {video_id} is not registered in active jobs.")

        job_info = self.active_jobs[video_id]
        start_time = job_info.get("submitted_at", time.time())

        while True:
            job = await self.jobs_api.get_task_status(video_id)
            if job.status == JobStatus.SUCCESS:
                elapsed_time = time.time() - start_time
                if not job.video_url:
                    raise ValueError(
                        f"Job {video_id} succeeded but returned no video URL."
                    )

                # Download asset
                dest_path = await self.downloads_api.download_asset(
                    url=job.video_url,
                    episode_id=job_info["episode_id"],
                    scene_id=job_info["scene_id"],
                    shot_id=job_info["shot_id"],
                    job=job,
                    elapsed_time=elapsed_time,
                    references=job_info["references"],
                )

                # Cleanup job tracking
                self.active_jobs.pop(video_id, None)
                self.persist_jobs()
                return dest_path

            elif job.status in (JobStatus.FAILED, JobStatus.MODERATION_FAILED):
                self.active_jobs.pop(video_id, None)
                self.persist_jobs()
                raise RuntimeError(
                    f"Job {video_id} failed with status: {job.status.name}"
                )

            await asyncio.sleep(polling_interval)

    async def run_queue(self, polling_interval: float = 5.0) -> list[Path]:
        """Process all tracked/checkpointed jobs in parallel
        (up to max_parallel_jobs).
        """
        results: list[Path] = []
        if not self.active_jobs:
            logger.info("No active jobs to process in queue.")
            return results

        semaphore = asyncio.Semaphore(self.max_parallel_jobs)

        async def worker(video_id: str):
            async with semaphore:
                try:
                    logger.info(
                        "Processing job in parallel queue worker", video_id=video_id
                    )
                    path = await self.poll_and_download(video_id, polling_interval)
                    results.append(path)
                except Exception as e:
                    logger.error(
                        "Error running queue worker for job",
                        video_id=video_id,
                        error=str(e),
                    )

        # Capture list of job keys since we modify active_jobs inside poll_and_download
        job_ids = list(self.active_jobs.keys())
        await asyncio.gather(*(worker(jid) for jid in job_ids))
        return results
