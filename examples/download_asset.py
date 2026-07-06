import asyncio
import sys

from pixverse.downloads import PixVerseDownloads
from pixverse.models import JobStatus, VideoJob


async def main():
    if len(sys.argv) < 3:
        print("Usage: python download_asset.py <video_url> <video_id>")
        return
    url = sys.argv[1]
    video_id = sys.argv[2]

    downloads = PixVerseDownloads()
    job = VideoJob(
        video_id=video_id,
        status=JobStatus.SUCCESS,
        prompt="Sample visual download",
        video_url=url,
        resolution="1080p",
        duration=5,
    )

    print(f"Downloading asset from {url}...")
    local_path = await downloads.download_asset(
        url=url,
        episode_id="1",
        scene_id="1",
        shot_id="1",
        job=job,
        elapsed_time=12.5,
    )
    print(f"Downloaded successfully! Local Path: {local_path}")
    await downloads.http_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
