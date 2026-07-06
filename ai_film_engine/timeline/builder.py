from typing import Any


class TimelineBuilder:
    def build_timeline(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Convert a compiled execution plan into a chronological timeline."""
        timeline_shots: list[dict[str, Any]] = []
        current_time = 0.0

        for job in plan["jobs"]:
            duration = float(job["duration"])
            start_time = current_time
            end_time = current_time + duration

            timeline_shots.append(
                {
                    "job_id": job["job_id"],
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "prompt": job["prompt"],
                    "output_path": job["output_path"],
                }
            )

            current_time = end_time

        return {
            "episode_id": plan["episode_id"],
            "title": plan["title"],
            "total_duration": current_time,
            "timeline": timeline_shots,
        }
