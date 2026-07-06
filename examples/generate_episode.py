import asyncio

from orchestrator.engine import OrchestratorEngine


async def main():
    # Make sure Episode001.json is compiled to output/ExecutionPlan.json first
    # using: python main.py compile Episode001.json
    engine = OrchestratorEngine(production=True)
    print("Starting generation loop with 2 workers...")
    await engine.run(max_workers=2)
    print("Generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
