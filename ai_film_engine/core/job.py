from typing import Any

from pydantic import BaseModel, Field


class Job(BaseModel):
    job_id: str
    job_type: str  # generate_image, generate_video, render, upscale, lip_sync, voice, subtitle, export
    status: str = "PENDING"  # PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    error_message: str | None = None
    retry_count: int = 0
