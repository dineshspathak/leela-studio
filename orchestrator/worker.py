import asyncio
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from config.logging import logger
from orchestrator.cache import AssetRegistry
from orchestrator.events import EventBus
from orchestrator.executor import OrchestratorExecutor
from orchestrator.queue import OrchestratorQueue, QueueState
from orchestrator.reporter import preporter


class LifecycleHooks:
    def __init__(self):
        self.before_generation_hooks: list[Callable] = []
        self.after_generation_hooks: list[Callable] = []
        self.before_download_hooks: list[Callable] = []
        self.after_download_hooks: list[Callable] = []

    def before_generation(self, job: dict[str, Any]):
        for h in self.before_generation_hooks:
            h(job)

    def after_generation(self, job: dict[str, Any], path: Path):
        for h in self.after_generation_hooks:
            h(job, path)

    def before_download(self, job: dict[str, Any]):
        for h in self.before_download_hooks:
            h(job)

    def after_download(self, job: dict[str, Any], path: Path):
        for h in self.after_download_hooks:
            h(job, path)


class OrchestratorWorker:
    def __init__(
        self,
        queue: OrchestratorQueue,
        executor: OrchestratorExecutor,
        event_bus: EventBus,
        hooks: LifecycleHooks,
        registry: AssetRegistry,
        production: bool = False,
        max_retries: int = 3,
    ):
        self.queue = queue
        self.executor = executor
        self.event_bus = event_bus
        self.hooks = hooks
        self.registry = registry
        self.production = production
        self.max_retries = max_retries
        self.lock = asyncio.Lock()

    async def start_worker_pool(self, num_workers: int = 2):
        """Spawn and manage worker pool concurrent tasks."""
        workers = [self._worker_loop(i) for i in range(num_workers)]
        await asyncio.gather(*workers)

    async def _worker_loop(self, worker_id: int):
        logger.info("Starting orchestrator queue worker", worker_id=worker_id)

        while True:
            job = None
            async with self.lock:
                # Find a READY job
                runnable = self.queue.get_runnable_jobs()
                if runnable:
                    job = runnable[0]
                    # Transition immediately to RUNNING to lock it
                    self.queue.update_job_status(job["job_id"], QueueState.RUNNING)

            if not job:
                # Check if all jobs in the queue are completed
                all_done = True
                for j in self.queue.jobs.values():
                    if j["status"] not in (
                        QueueState.SUCCESS,
                        QueueState.FAILED,
                        QueueState.CANCELLED,
                    ):
                        all_done = False
                        break

                if all_done:
                    logger.info(
                        "Worker finished: Queue is fully processed", worker_id=worker_id
                    )
                    break

                # Otherwise wait for dependencies to clear
                await asyncio.sleep(1.0)
                continue

            job_id = job["job_id"]
            logger.info("Worker picked up job", worker_id=worker_id, job_id=job_id)
            await self.event_bus.emit("JOB_STARTED", job)

            # Smart Asset Reuse Cache check
            prompt_hash = self.registry.generate_prompt_hash(job)
            cached_path = self.registry.get_cached_asset(prompt_hash)

            if cached_path and self.production:
                logger.info(
                    "Cache hit! Reusing existing asset", job_id=job_id, path=cached_path
                )
                preporter.add_metric("cache_hits", 1)
                await self.event_bus.emit("CACHE_HIT", job)
                self.queue.update_job_status(job_id, QueueState.SUCCESS)
                continue

            preporter.add_metric("cache_misses", 1)
            await self.event_bus.emit("CACHE_MISS", job)

            # Execution with Retry Policy
            retry_count = 0
            backoff = 2.0
            success = False

            while retry_count <= self.max_retries:
                try:
                    self.hooks.before_generation(job)

                    # Call execution
                    local_path = await self.executor.execute_job(job)

                    self.hooks.before_download(job)
                    self.hooks.after_download(job, local_path)
                    self.hooks.after_generation(job, local_path)

                    # Register asset details
                    metadata = {
                        "provider": job.get("provider", "pixverse"),
                        "resolution": "720p",
                        "duration": job.get("duration", 5),
                        "references": job.get("references", []),
                        "created_at": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                        ),
                    }
                    self.registry.register_asset(prompt_hash, local_path, job, metadata)

                    await self.event_bus.emit("DOWNLOAD_COMPLETED", job)
                    await self.event_bus.emit("JOB_COMPLETED", job)

                    self.queue.update_job_status(job_id, QueueState.SUCCESS)
                    success = True
                    break

                except Exception as e:
                    retry_count += 1
                    logger.error(
                        "Job execution attempt failed",
                        job_id=job_id,
                        attempt=retry_count,
                        error=str(e),
                    )
                    preporter.record_failure(job_id, str(e), retry_count, exception=e)

                    if retry_count > self.max_retries or not self.production:
                        break

                    await self.event_bus.emit("JOB_RETRY", job)
                    sleep_time = backoff**retry_count
                    logger.info(f"Worker sleeping for {sleep_time}s before retry")
                    await asyncio.sleep(sleep_time)

            if not success:
                logger.error("Job permanently failed", job_id=job_id)
                self.queue.update_job_status(
                    job_id, QueueState.FAILED, "Max retries exceeded"
                )
                await self.event_bus.emit("JOB_FAILED", job)
