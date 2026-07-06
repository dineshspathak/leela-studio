import os
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PixVerseSettings(BaseModel):
    api_key: str = Field(default="")
    base_url: str = Field(default="https://app-api.pixverse.ai/openapi/v2")
    timeout: float = Field(default=30.0)
    retries: int = Field(default=3)
    polling_interval: float = Field(default=5.0)
    max_parallel_jobs: int = Field(default=2)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    pixverse: PixVerseSettings = Field(default_factory=PixVerseSettings)


def load_settings(yaml_path: Path = Path("config/settings.yaml")) -> Settings:
    # Read yaml
    if yaml_path.exists():
        with open(yaml_path, encoding="utf-8") as f:
            content = f.read()

            # Replace environment variables e.g. ${VAR} or $VAR
            def replacer(match):
                var_name = match.group(1) or match.group(2)
                return os.getenv(var_name, "")

            content = re.sub(r"\$\{(\w+)\}|\$(\w+)", replacer, content)
            yaml_data = yaml.safe_load(content) or {}
    else:
        yaml_data = {}

    pixverse_data = yaml_data.get("pixverse", {}) or {}

    # Allow explicit environment override
    if os.getenv("PIXVERSE_API_KEY"):
        pixverse_data["api_key"] = os.getenv("PIXVERSE_API_KEY")
    if os.getenv("PIXVERSE_BASE_URL"):
        pixverse_data["base_url"] = os.getenv("PIXVERSE_BASE_URL")

    return Settings(pixverse=PixVerseSettings(**pixverse_data))


# Instantiate settings
settings = load_settings()
