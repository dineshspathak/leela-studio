from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    description: str | None = None
    costume: str | None = None
    master_asset_id: str | None = None


class Location(BaseModel):
    name: str
    environment: str | None = "indoor"
    lighting_default: str | None = "natural"
    master_asset_id: str | None = None


class Asset(BaseModel):
    id: str
    name: str
    type: str  # image, video, audio
    local_path: str


class Music(BaseModel):
    name: str
    path: str | None = None
    volume: float = 0.5


class SFX(BaseModel):
    name: str
    path: str | None = None
    delay: float = 0.0


class Narration(BaseModel):
    text: str
    voice_id: str | None = None


class Shot(BaseModel):
    episode_id: str | None = None
    scene_id: str | None = None
    shot_id: str
    title: str
    duration: int | None = None
    provider: str | None = None
    generation_type: str  # text_to_image, image_to_video, text_to_video, existing_asset
    prompt: str
    negative_prompt: str | None = None
    references: list[str] = Field(default_factory=list)
    camera: str | None = None
    motion: str | None = None
    characters: list[str] = Field(default_factory=list)
    location: str | None = None
    music: Music | None = None
    sfx: list[SFX] = Field(default_factory=list)
    narration: Narration | None = None
    output_filename: str | None = None


class Scene(BaseModel):
    scene_id: str
    title: str
    location: str | None = None
    camera_default: str | None = None
    lighting_default: str | None = None
    duration_default: int | None = None
    provider_default: str | None = None
    negative_prompt_default: str | None = None
    shots: list[Shot] = Field(default_factory=list)


class GlobalDefaults(BaseModel):
    resolution: str = "720p"
    aspect_ratio: str = "16:9"
    fps: int = 24
    provider: str = "pixverse"
    camera_style: str = "static"
    visual_style: str = "photorealistic 3D animation"
    cinematic_profile: str = "volumetric lighting, highly detailed"
    negative_prompt: str = "ugly, deformed, blurry, low resolution, watermark"


class Episode(BaseModel):
    episode_id: str
    title: str
    variables: dict[str, str] = Field(default_factory=dict)
    global_defaults: GlobalDefaults = Field(default_factory=GlobalDefaults)
    characters: list[Character] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)
