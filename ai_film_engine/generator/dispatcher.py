from typing import Any


class ProviderHealthManager:
    def __init__(self):
        self.health_states: dict[str, dict[str, Any]] = {
            "pixverse": {
                "status": "healthy",
                "response_time": 0.1,
                "rate_limit": 60,
                "daily_quota": 500,
                "estimated_queue_time": 1.0,
            },
            "google_veo": {
                "status": "healthy",
                "response_time": 0.2,
                "rate_limit": 30,
                "daily_quota": 100,
                "estimated_queue_time": 2.0,
            },
            "runway": {
                "status": "unhealthy",
                "response_time": 1.5,
                "rate_limit": 10,
                "daily_quota": 50,
                "estimated_queue_time": 10.0,
            },
        }

    def check_health(self) -> dict[str, dict[str, Any]]:
        return self.health_states

    def update_health(self, provider: str, status: str, response_time: float):
        if provider in self.health_states:
            self.health_states[provider]["status"] = status
            self.health_states[provider]["response_time"] = response_time


class AdaptiveScheduler:
    def __init__(self, health_manager: ProviderHealthManager):
        self.health_manager = health_manager

    def schedule_jobs(self, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Adaptive rebalancing of jobs to healthy alternative providers."""
        health = self.health_manager.check_health()
        scheduled_jobs = []

        for job in jobs:
            provider = job.get("provider")
            # If target provider is unhealthy, rebalance/move to healthy alternative
            if health.get(provider, {}).get("status") != "healthy":
                # Find healthy provider
                alternative = "pixverse"
                for p, hs in health.items():
                    if hs["status"] == "healthy":
                        alternative = p
                        break
                job["provider"] = alternative
            scheduled_jobs.append(job)

        return scheduled_jobs
