import asyncio

from pixverse.client import PixVerseClient
from pixverse.jobs import PixVerseJobs
from pixverse.schemas import TextToVideoRequest


async def main():
    async with PixVerseClient() as client:
        jobs = PixVerseJobs(client)
        req = TextToVideoRequest(
            prompt="Volumetric lightning strike illuminating the Yamuna river parting",
            quality="1080p",
            aspect_ratio="16:9",
            duration=8,
        )
        print("Submitting text-to-video generation request...")
        job = await jobs.generate_text_to_video(req)
        print(f"Submitted successfully! Task ID: {job.video_id}")


if __name__ == "__main__":
    asyncio.run(main())
