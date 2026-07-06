import asyncio
import sys

from pixverse.client import PixVerseClient
from pixverse.jobs import PixVerseJobs


async def main():
    if len(sys.argv) < 2:
        print("Usage: python check_status.py <video_id>")
        return
    video_id = sys.argv[1]
    async with PixVerseClient() as client:
        jobs = PixVerseJobs(client)
        print(f"Retrieving status for job {video_id}...")
        job = await jobs.get_task_status(video_id)
        print(f"Status: {job.status.name}")
        if job.video_url:
            print(f"Download URL: {job.video_url}")


if __name__ == "__main__":
    asyncio.run(main())
