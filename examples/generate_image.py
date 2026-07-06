import asyncio

from pixverse.client import PixVerseClient
from pixverse.jobs import PixVerseJobs


async def main():
    # Make sure to set PIXVERSE_API_KEY env or configure it in config/settings.yaml
    async with PixVerseClient() as client:
        jobs = PixVerseJobs(client)
        print("Submitting text-to-image generation request...")
        job = await jobs.generate_image(
            "A serene visual of Baby Krishna sleeping in a cradle"
        )
        print(f"Submitted successfully! Task ID: {job.video_id}")


if __name__ == "__main__":
    asyncio.run(main())
