import asyncio

from pixverse.client import PixVerseClient
from pixverse.jobs import PixVerseJobs
from pixverse.schemas import ImageToVideoRequest


async def main():
    async with PixVerseClient() as client:
        jobs = PixVerseJobs(client)
        req = ImageToVideoRequest(
            prompt="Slow pan of Sheshnag serpent shielding Devaki's baby from storm",
            image_url="https://raw.githubusercontent.com/dineshspathak/leela-studio/main/LEELA/Assets/Backgrounds/Prison/prison_cell_wide_establishing.png",
        )
        print("Submitting image-to-video generation request...")
        job = await jobs.generate_image_to_video(req)
        print(f"Submitted successfully! Task ID: {job.video_id}")


if __name__ == "__main__":
    asyncio.run(main())
