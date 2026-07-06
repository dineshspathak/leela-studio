from pydantic import BaseModel, Field


class TextToVideoRequest(BaseModel):
    prompt: str
    model: str = "v6"
    duration: int = 5
    quality: str = "720p"
    aspect_ratio: str = "16:9"
    motion_mode: str = "normal"
    seed: int | None = None
    negative_prompt: str | None = None
    water_mark: bool = False


class ImageToVideoRequest(BaseModel):
    prompt: str
    image_url: str
    model: str = "v6"
    duration: int = 5
    quality: str = "720p"
    aspect_ratio: str = "16:9"
    motion_mode: str = "normal"
    seed: int | None = None
    negative_prompt: str | None = None
    water_mark: bool = False


class PixVerseResponseData(BaseModel):
    model_config = {"populate_by_name": True}
    video_id: str | None = Field(default=None, alias="video_id")
    status: int | None = Field(default=None, alias="status")
    video_url: str | None = Field(default=None, alias="video_url")
    seed: int | None = Field(default=None, alias="seed")
    duration: int | None = Field(default=None, alias="duration")
    resolution: str | None = Field(default=None, alias="resolution")
    created_at: str | None = Field(default=None, alias="created_at")


class PixVerseEnvelope(BaseModel):
    model_config = {"populate_by_name": True}
    code: int = Field(alias="ErrCode")
    msg: str = Field(alias="ErrMsg")
    data: PixVerseResponseData | None = Field(default=None, alias="Resp")
