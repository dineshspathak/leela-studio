from typing import Any

from pydantic import BaseModel, Field


class Asset(BaseModel):
    asset_id: str
    asset_type: (
        str  # image, video, audio, subtitle, prompt, lora, style, template, model
    )
    path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class ImageAsset(Asset):
    resolution: str
    format: str


class VideoAsset(Asset):
    resolution: str
    duration: float
    fps: int


class AudioAsset(Asset):
    sample_rate: int
    duration: float
    channels: int
