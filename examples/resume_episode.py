import asyncio

from orchestrator.engine import OrchestratorEngine


async def main():
    engine = OrchestratorEngine(production=True)
    print("Resuming execution from checkpoint...")
    await engine.run(max_workers=2)
    print("Resumed execution complete!")


if __name__ == "__main__":
    asyncio.run(main())
