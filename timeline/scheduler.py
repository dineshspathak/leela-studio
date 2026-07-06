from collections import deque
from typing import Any


class CostEstimator:
    def __init__(
        self, image_cost: int = 1, video_cost: int = 10, sec_runtime: float = 12.0
    ):
        self.image_cost = image_cost
        self.video_cost = video_cost
        self.sec_runtime = sec_runtime

    def estimate_costs(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Estimate required API calls, total runtime, and PixVerse credit consumption."""
        num_images = 0
        num_img_to_vid = 0
        num_txt_to_vid = 0

        for job in plan["jobs"]:
            gen_type = job["generation_type"]
            if gen_type == "text_to_image":
                num_images += 1
            elif gen_type == "image_to_video":
                num_img_to_vid += 1
            elif gen_type == "text_to_video":
                num_txt_to_vid += 1

        total_credits = (num_images * self.image_cost) + (
            (num_img_to_vid + num_txt_to_vid) * self.video_cost
        )
        total_runtime = (
            num_images + num_img_to_vid + num_txt_to_vid
        ) * self.sec_runtime

        return {
            "estimated_images": num_images,
            "estimated_image_to_video": num_img_to_vid,
            "estimated_text_to_video": num_txt_to_vid,
            "total_estimated_credits": total_credits,
            "estimated_runtime_seconds": total_runtime,
        }


class ExecutionScheduler:
    def schedule_jobs(self, plan: dict[str, Any], graph: dict[str, Any]) -> list[str]:
        """Compute the topological ordering (execution schedule) of jobs based on dependencies."""
        in_degree: dict[str, int] = dict.fromkeys(graph["nodes"], 0)
        adj_list: dict[str, list[str]] = {node: [] for node in graph["nodes"]}

        for edge in graph["edges"]:
            u = edge["from"]
            v = edge["to"]
            if u in adj_list and v in adj_list:
                adj_list[u].append(v)
                in_degree[v] += 1

        # Simple queue for topological ordering
        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return order
