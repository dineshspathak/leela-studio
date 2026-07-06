import json
from pathlib import Path

import httpx
import pytest
import respx

from config.settings import load_settings
from pixverse.auth import PixVerseAuth
from pixverse.client import PixVerseClient
from pixverse.downloads import PixVerseDownloads
from pixverse.exceptions import (
    PixVerseAuthError,
    PixVerseRateLimitError,
)
from pixverse.jobs import JobManager, PixVerseJobs
from pixverse.models import JobStatus, VideoJob
from pixverse.schemas import ImageToVideoRequest, TextToVideoRequest
from providers.pixverse import PixVerseProvider


@pytest.fixture
def test_settings():
    return load_settings(Path("config/settings.yaml"))


@pytest.fixture
def auth():
    return PixVerseAuth(api_key="test_key")


@pytest.mark.asyncio
async def test_auth_headers(auth):
    headers = auth.get_headers(trace_id="trace_123")
    assert headers["API-KEY"] == "test_key"
    assert headers["Ai-trace-id"] == "trace_123"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
@respx.mock
async def test_client_requests():
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2"
    )

    # Mock health endpoint
    respx.get("https://app-api.pixverse.ai/openapi/v2/health").mock(
        return_value=httpx.Response(200, json={"code": 0, "msg": "success"})
    )

    jobs = PixVerseJobs(client)
    health = await jobs.health_check()
    assert health is True
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_client_rate_limit_and_error():
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2", retries=1
    )

    # Mock rate limit
    respx.get("https://app-api.pixverse.ai/openapi/v2/health").mock(
        return_value=httpx.Response(429, text="Rate limit exceeded")
    )

    with pytest.raises(PixVerseRateLimitError):
        await client._request("GET", "/health")
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_client_auth_error():
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2", retries=0
    )
    respx.get("https://app-api.pixverse.ai/openapi/v2/health").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with pytest.raises(PixVerseAuthError):
        await client._request("GET", "/health")
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_jobs_submission():
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2"
    )

    # Text to video mock
    respx.post("https://app-api.pixverse.ai/openapi/v2/video/text/generate").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "msg": "success", "data": {"video_id": "vid_123"}}
        )
    )
    # Image to video mock
    respx.post("https://app-api.pixverse.ai/openapi/v2/video/img/generate").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "msg": "success", "data": {"video_id": "vid_456"}}
        )
    )
    # Image generation mock
    respx.post("https://app-api.pixverse.ai/openapi/v2/image/generate").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "msg": "success", "data": {"video_id": "vid_789"}}
        )
    )

    jobs = PixVerseJobs(client)

    t2v_job = await jobs.generate_text_to_video(
        TextToVideoRequest(prompt="test prompt")
    )
    assert t2v_job.video_id == "vid_123"

    i2v_job = await jobs.generate_image_to_video(
        ImageToVideoRequest(prompt="test prompt", image_url="http://test.com/img.png")
    )
    assert i2v_job.video_id == "vid_456"

    img_job = await jobs.generate_image("test prompt")
    assert img_job.video_id == "vid_789"

    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_get_status_and_cancel():
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2"
    )

    respx.get("https://app-api.pixverse.ai/openapi/v2/video/result/vid_123").mock(
        return_value=httpx.Response(
            200,
            json={
                "code": 0,
                "msg": "success",
                "data": {
                    "video_id": "vid_123",
                    "status": 1,
                    "video_url": "http://test.com/out.mp4",
                    "seed": 42,
                    "duration": 5,
                    "resolution": "720p",
                    "created_at": "2026-07-06T10:00:00Z",
                },
            },
        )
    )

    respx.post("https://app-api.pixverse.ai/openapi/v2/video/cancel").mock(
        return_value=httpx.Response(200, json={"code": 0, "msg": "success"})
    )

    jobs = PixVerseJobs(client)
    job = await jobs.get_task_status("vid_123")
    assert job.status == JobStatus.SUCCESS
    assert job.video_url == "http://test.com/out.mp4"
    assert job.seed == 42

    canceled = await jobs.cancel_task("vid_123")
    assert canceled is True
    await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_download_manager(tmp_path):
    downloads = PixVerseDownloads()

    # Mock file download stream
    respx.get("http://test.com/out.mp4").mock(
        return_value=httpx.Response(200, content=b"fake_video_data")
    )

    job = VideoJob(
        video_id="vid_123",
        status=JobStatus.SUCCESS,
        prompt="test prompt",
        video_url="http://test.com/out.mp4",
        seed=100,
        duration=5,
        resolution="720p",
        created_at="2026-07-06",
    )

    dest_path = await downloads.download_asset(
        url="http://test.com/out.mp4",
        episode_id="1",
        scene_id="2",
        shot_id="3",
        job=job,
        elapsed_time=15.0,
        base_dir=str(tmp_path),
    )

    assert dest_path.exists()
    assert dest_path.name == "Shot003.mp4"
    assert (tmp_path / "Episode001" / "Scene002" / "Shot003_asset.json").exists()

    # Validate json content
    with open(tmp_path / "Episode001" / "Scene002" / "Shot003_asset.json") as f:
        meta = json.load(f)
    assert meta["job_id"] == "vid_123"
    assert meta["generation_time"] == 15.0
    await downloads.http_client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_job_manager_checkpoint(tmp_path):
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2"
    )
    jobs = PixVerseJobs(client)
    downloads = PixVerseDownloads()

    checkpoint_file = tmp_path / "active_jobs.json"

    # Mock submissions
    respx.post("https://app-api.pixverse.ai/openapi/v2/video/text/generate").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "msg": "success", "data": {"video_id": "vid_999"}}
        )
    )

    manager = JobManager(
        jobs_api=jobs, downloads_api=downloads, active_jobs_file=str(checkpoint_file)
    )

    req = TextToVideoRequest(prompt="checkpoint prompt")
    await manager.submit_text_to_video(req, "1", "1", "1")

    assert "vid_999" in manager.active_jobs
    assert checkpoint_file.exists()

    # Create new manager to check checkpoint restore
    new_manager = JobManager(
        jobs_api=jobs, downloads_api=downloads, active_jobs_file=str(checkpoint_file)
    )
    assert "vid_999" in new_manager.active_jobs

    await client.close()
    await downloads.http_client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_provider_wrapper():
    client = PixVerseClient(
        api_key="test_key", base_url="https://app-api.pixverse.ai/openapi/v2"
    )
    provider = PixVerseProvider(client)

    respx.post("https://app-api.pixverse.ai/openapi/v2/video/text/generate").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "msg": "success", "data": {"video_id": "vid_ok"}}
        )
    )

    job = await provider.generate_text_to_video(
        TextToVideoRequest(prompt="provider test")
    )
    assert job.video_id == "vid_ok"

    authenticated = await provider.authenticate()
    assert authenticated is True

    await client.close()
