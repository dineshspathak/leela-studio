import time

from pydantic import BaseModel, Field


class AssetLineage(BaseModel):
    asset_id: str
    parent_assets: list[str] = Field(default_factory=list)
    parent_prompts: list[str] = Field(default_factory=list)
    provider: str
    model: str
    seed: int | None = None
    workflow: str
    episode: str
    scene: str
    shot: str
    timestamp: float = Field(default_factory=time.time)


class GenerationTracker:
    def __init__(self):
        self.states: dict[str, str] = {}  # job_id -> status
        self.lineages: dict[str, AssetLineage] = {}

    def update_status(self, job_id: str, status: str):
        self.states[job_id] = status

    def register_lineage(self, asset_id: str, lineage: AssetLineage):
        self.lineages[asset_id] = lineage

    def get_status(self, job_id: str) -> str:
        return self.states.get(job_id, "QUEUED")
