import json
from pathlib import Path
from typing import Any


class QueueState:
    READY = "READY"
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"

class OrchestratorQueue:
    def __init__(self, checkpoint_file: str = "cache/orchestrator_queue.json"):
        self.checkpoint_file = Path(checkpoint_file)
        self.jobs: dict[str, dict[str, Any]] = {}
        self.dependencies: dict[str, list[str]] = {} # job_id -> list of parent job_ids

    def add_job(
        self,
        job_id: str,
        job_info: dict[str, Any],
        deps: list[str] | None = None,
    ):
        self.jobs[job_id] = {
            **job_info,
            "status": QueueState.WAITING if deps else QueueState.READY,
            "error_msg": None,
            "retry_count": 0,
        }
        self.dependencies[job_id] = deps or []

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return self.jobs.get(job_id)

    def update_job_status(
        self, job_id: str, status: str, error_msg: str | None = None
    ):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            if error_msg:
                self.jobs[job_id]["error_msg"] = error_msg

            # If a job succeeds, update other WAITING jobs that depend on it
            if status == QueueState.SUCCESS:
                for jid, deps in self.dependencies.items():
                    if (
                        self.jobs[jid]["status"] == QueueState.WAITING
                        and all(
                            self.jobs.get(d, {}).get("status")
                            == QueueState.SUCCESS
                            for d in deps
                        )
                    ):
                        self.jobs[jid]["status"] = QueueState.READY

            self.persist_checkpoint()

    def get_runnable_jobs(self) -> list[dict[str, Any]]:
        """Return all jobs in READY state."""
        return [job for job in self.jobs.values() if job["status"] == QueueState.READY]

    def persist_checkpoint(self):
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "jobs": self.jobs,
            "dependencies": self.dependencies,
        }
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def load_checkpoint(self) -> bool:
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, encoding="utf-8") as f:
                    state = json.load(f)
                self.jobs = state["jobs"]
                self.dependencies = state["dependencies"]
                return True
            except Exception:
                pass
        return False

    def clear_checkpoint(self):
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        self.jobs = {}
        self.dependencies = {}
