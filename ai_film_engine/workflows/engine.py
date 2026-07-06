import asyncio
from collections import deque

from ai_film_engine.core.job import Job


class WorkflowEngine:
    def __init__(self):
        self.jobs: dict[str, Job] = {}

    def add_job(self, job: Job):
        self.jobs[job.job_id] = job

    async def execute_workflow(self) -> dict[str, str]:
        """Execute a graph of jobs in topological order."""
        # Simple topological sort
        in_degree = dict.fromkeys(self.jobs, 0)
        adj_list = {jid: [] for jid in self.jobs}

        for jid, job in self.jobs.items():
            for dep in job.dependencies:
                if dep in self.jobs:
                    adj_list[dep].append(jid)
                    in_degree[jid] += 1

        queue = deque([jid for jid, deg in in_degree.items() if deg == 0])
        results: dict[str, str] = {}

        while queue:
            jid = queue.popleft()
            job = self.jobs[jid]

            # Execute mock job action
            job.status = "RUNNING"
            await asyncio.sleep(0.01)  # Simulate execution
            job.status = "SUCCESS"
            results[jid] = "SUCCESS"

            for neighbor in adj_list[jid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return results
