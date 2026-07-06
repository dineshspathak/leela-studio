import json
import traceback
from pathlib import Path
from typing import Any


class Reporter:
    def __init__(
        self,
        failures_log: str = "logs/failures.json",
        metrics_log: str = "metrics.json",
    ):
        self.failures_log = Path(failures_log)
        self.metrics_log = Path(metrics_log)

        # Init metrics state
        self.metrics: dict[str, Any] = {
            "generation_time": 0.0,
            "download_time": 0.0,
            "api_latency": 0.0,
            "queue_wait_time": 0.0,
            "credits_used": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        self._load_metrics()

    def _load_metrics(self):
        if self.metrics_log.exists():
            try:
                with open(self.metrics_log, encoding="utf-8") as f:
                    self.metrics = json.load(f)
            except Exception:
                pass

    def save_metrics(self):
        self.metrics_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metrics_log, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2)

    def add_metric(self, key: str, value: Any):
        if key in self.metrics:
            if isinstance(self.metrics[key], (int, float)):
                self.metrics[key] += value
            else:
                self.metrics[key] = value
        self.save_metrics()

    def record_failure(
        self,
        job_id: str,
        reason: str,
        retry_count: int,
        provider_response: str = "",
        exception: Exception | None = None,
    ):
        self.failures_log.parent.mkdir(parents=True, exist_ok=True)
        failures = []

        if self.failures_log.exists():
            try:
                with open(self.failures_log, encoding="utf-8") as f:
                    failures = json.load(f)
            except Exception:
                failures = []

        stack = ""
        if exception:
            stack = "".join(
                traceback.format_exception(None, exception, exception.__traceback__)
            )

        failure_record = {
            "job_id": job_id,
            "reason": reason,
            "stacktrace": stack,
            "retry_count": retry_count,
            "provider_response": provider_response,
        }
        failures.append(failure_record)

        with open(self.failures_log, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2)


preporter = Reporter()
