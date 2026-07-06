from typing import Any

from pydantic import BaseModel, Field


class EffectPlugin(BaseModel):
    name: str
    params: dict[str, Any] = Field(default_factory=dict)


class Clip(BaseModel):
    clip_id: str
    start_time: float
    end_time: float
    asset_path: str
    volume: float = 1.0
    effects: list[EffectPlugin] = Field(default_factory=list)
    transition: str | None = None
    transition_duration: float = 0.5


class Track(BaseModel):
    track_id: str
    track_type: str  # video, audio, subtitle
    clips: list[Clip] = Field(default_factory=list)


class SceneGraph(BaseModel):
    scene_id: str
    tracks: list[Track] = Field(default_factory=list)
