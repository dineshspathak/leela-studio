import asyncio
import time
from pathlib import Path
from typing import Any

from ai_film_engine.core.config.settings import settings
from ai_film_engine.orchestrator.reporter import preporter
from ai_film_engine.providers.pixverse.client import PixVerseClient
from ai_film_engine.providers.pixverse.schemas import (
    ImageToVideoRequest,
    TextToVideoRequest,
)
from ai_film_engine.providers.pixverse_provider import PixVerseProvider


class OrchestratorExecutor:
    def __init__(self, provider: Any = None):
        self.provider = provider

    async def execute_job(self, job: dict[str, Any]) -> Path:
        """Call the Provider interface to execute the job."""
        gen_type = job["generation_type"]
        prompt = job["prompt"]
        neg_prompt = job["negative_prompt"]
        duration = job["duration"]
        references = job["references"]
        output_path = job["output_path"]

        if not self.provider:
            # Lazy initialize if no provider is injected
            client = PixVerseClient()
            self.provider = PixVerseProvider(client)

        start_time = time.perf_counter()

        if gen_type == "text_to_image":
            res_job = await self.provider.generate_image(prompt)
        elif gen_type == "image_to_video":
            image_url = references[0] if references else ""
            req = ImageToVideoRequest(
                prompt=prompt,
                image_url=image_url,
                duration=duration,
                negative_prompt=neg_prompt,
            )
            res_job = await self.provider.generate_image_to_video(req)
        elif gen_type == "text_to_video":
            req = TextToVideoRequest(
                prompt=prompt,
                duration=duration,
                negative_prompt=neg_prompt,
            )
            res_job = await self.provider.generate_text_to_video(req)
        else:
            raise ValueError(f"Unsupported generation type: {gen_type}")

        # Poll status until complete
        while True:
            status_job = await self.provider.get_task_status(res_job.video_id)
            if status_job.status.name == "SUCCESS":
                elapsed = time.perf_counter() - start_time
                preporter.add_metric("generation_time", elapsed)

                # Download asset to structured location
                download_start = time.perf_counter()
                path_parts = Path(output_path).parts
                # Fallback zfilling to build clean paths
                episode_id = path_parts[1] if len(path_parts) > 1 else "1"
                scene_id = path_parts[2] if len(path_parts) > 2 else "1"
                shot_id = Path(output_path).stem

                local_path = await self.provider.download_asset(
                    url=status_job.video_url,
                    episode_id=episode_id,
                    scene_id=scene_id,
                    shot_id=shot_id,
                    job=status_job,
                    elapsed_time=elapsed,
                    references=references,
                )
                download_elapsed = time.perf_counter() - download_start
                preporter.add_metric("download_time", download_elapsed)
                return local_path

            elif status_job.status.name in ("FAILED", "MODERATION_FAILED"):
                raise RuntimeError(
                    f"Generation failed: {status_job.error_message or 'Moderation fail or API error'}"
                )

            await asyncio.sleep(settings.pixverse.polling_interval)
