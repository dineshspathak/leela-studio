import json
from pathlib import Path
from typing import Any


class BudgetManager:
    def __init__(
        self,
        budget_file: str = "cache/budget_state.json",
        daily_limit: int = 100,
        episode_limit: int = 500,
        monthly_limit: int = 2000,
    ):
        self.budget_file = Path(budget_file)
        self.daily_limit = daily_limit
        self.episode_limit = episode_limit
        self.monthly_limit = monthly_limit

        # Load state
        self.state = {
            "daily_used": 0,
            "episode_used": 0,
            "monthly_used": 0,
        }
        self.load_state()

    def load_state(self):
        if self.budget_file.exists():
            try:
                with open(self.budget_file, encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                pass

    def save_state(self):
        self.budget_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.budget_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def deduct_credits(self, amount: int):
        self.state["daily_used"] += amount
        self.state["episode_used"] += amount
        self.state["monthly_used"] += amount
        self.save_state()

    def check_budget_limit(self, estimated_cost: int) -> bool:
        """Returns True if within limits, False if limits would be exceeded."""
        if self.state["daily_used"] + estimated_cost > self.daily_limit:
            return False
        if self.state["episode_used"] + estimated_cost > self.episode_limit:
            return False
        return self.state["monthly_used"] + estimated_cost <= self.monthly_limit

    def get_summary(self) -> dict[str, Any]:
        return {
            "daily_limit": self.daily_limit,
            "daily_used": self.state["daily_used"],
            "episode_limit": self.episode_limit,
            "episode_used": self.state["episode_used"],
            "monthly_limit": self.monthly_limit,
            "monthly_used": self.state["monthly_used"],
        }
