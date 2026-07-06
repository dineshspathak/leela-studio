from pydantic import BaseModel


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
    video_id: str
    status: int | None = None
    video_url: str | None = None
    seed: int | None = None
    duration: int | None = None
    resolution: str | None = None
    created_at: str | None = None


class PixVerseEnvelope(BaseModel):
    code: int
    msg: str
    data: PixVerseResponseData | None = None
