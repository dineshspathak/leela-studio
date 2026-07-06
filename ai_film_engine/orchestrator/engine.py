import json
import time
from pathlib import Path
from typing import Any

from ai_film_engine.budget.manager import BudgetManager
from ai_film_engine.core.config.logging import logger
from ai_film_engine.orchestrator.cache import AssetRegistry
from ai_film_engine.orchestrator.events import EventBus
from ai_film_engine.orchestrator.executor import OrchestratorExecutor
from ai_film_engine.orchestrator.monitor import start_dashboard
from ai_film_engine.orchestrator.queue import OrchestratorQueue, QueueState
from ai_film_engine.orchestrator.worker import LifecycleHooks, OrchestratorWorker


class OrchestratorEngine:
    def __init__(
        self,
        plan_path: str = "output/ExecutionPlan.json",
        graph_path: str = "output/ExecutionGraph.json",
        production: bool = False,
    ):
        self.plan_path = Path(plan_path)
        self.graph_path = Path(graph_path)
        self.production = production

        self.queue = OrchestratorQueue()
        self.budget = BudgetManager()
        self.registry = AssetRegistry()
        self.event_bus = EventBus()
        self.hooks = LifecycleHooks()
        self.executor = OrchestratorExecutor()

        self.is_running = False
        self.current_episode_id = "1"
        self.start_time = 0.0

    def get_progress(self) -> dict[str, Any]:
        total = len(self.queue.jobs)
        if total == 0:
            return {}
        completed = sum(
            1 for j in self.queue.jobs.values() if j["status"] == QueueState.SUCCESS
        )
        failed = sum(
            1 for j in self.queue.jobs.values() if j["status"] == QueueState.FAILED
        )
        running = sum(
            1 for j in self.queue.jobs.values() if j["status"] == QueueState.RUNNING
        )

        percent = (completed / total) * 100.0
        elapsed = time.time() - self.start_time if self.is_running else 0.0
        eta = (elapsed / completed) * (total - completed) if completed > 0 else 0.0

        return {
            "episode_completed_percent": percent,
            "total_jobs": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "elapsed_seconds": elapsed,
            "eta_seconds": eta,
        }

    async def run(self, max_workers: int = 2, force: bool = False):
        if not self.plan_path.exists() or not self.graph_path.exists():
            raise FileNotFoundError(
                "Execution plan and graph files must be compiled first."
            )

        with open(self.plan_path, encoding="utf-8") as f:
            plan = json.load(f)
        with open(self.graph_path, encoding="utf-8") as f:
            graph = json.load(f)

        self.current_episode_id = plan.get("episode_id", "1")
        self.start_time = time.time()
        self.is_running = True

        # Load checkpoint or rebuild queue
        checkpoint_loaded = False
        if self.production:
            checkpoint_loaded = self.queue.load_checkpoint()

        if not checkpoint_loaded:
            self.queue.clear_checkpoint()
            for job in plan["jobs"]:
                job_id = job["job_id"]
                deps = [e["from"] for e in graph["edges"] if e["to"] == job_id]
                self.queue.add_job(job_id, job, deps)

        # Budget manager check
        estimated_cost = 0
        for job in self.queue.jobs.values():
            if job["status"] not in (QueueState.SUCCESS, QueueState.CANCELLED):
                gen_type = job["generation_type"]
                estimated_cost += 1 if gen_type == "text_to_image" else 10

        if self.production and not self.budget.check_budget_limit(estimated_cost):
            logger.error("Budget limit exceeded! Pausing execution automatically.")
            await self.event_bus.emit("BUDGET_WARNING", self.budget.get_summary())
            self.is_running = False
            return

        # Start API server dashboard in background on port 8080
        server = start_dashboard(self.queue, self.budget, self, port=8080)

        # Spawning workers
        worker = OrchestratorWorker(
            queue=self.queue,
            executor=self.executor,
            event_bus=self.event_bus,
            hooks=self.hooks,
            registry=self.registry,
            production=self.production,
        )

        try:
            await self.event_bus.emit("before_episode", plan)
            await worker.start_worker_pool(num_workers=max_workers)
            await self.event_bus.emit("after_episode", plan)
        finally:
            self.is_running = False
            server.shutdown()
