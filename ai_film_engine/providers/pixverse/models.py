from enum import IntEnum

from pydantic import BaseModel


class JobStatus(IntEnum):
    SUCCESS = 1
    GENERATING = 5
    MODERATION_FAILED = 7
    FAILED = 8


class VideoJob(BaseModel):
    video_id: str
    status: JobStatus = JobStatus.GENERATING
    prompt: str
    video_url: str | None = None
    seed: int | None = None
    duration: int | None = None
    resolution: str | None = None
    created_at: str | None = None
    error_message: str | None = None
