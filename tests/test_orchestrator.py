from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from budget.manager import BudgetManager
from main import app
from orchestrator.cache import AssetRegistry
from orchestrator.engine import OrchestratorEngine
from orchestrator.events import EventBus
from orchestrator.executor import OrchestratorExecutor
from orchestrator.queue import OrchestratorQueue, QueueState

runner = CliRunner()


@pytest.fixture
def clean_cache(tmp_path):
    db = tmp_path / "assets.db"
    js = tmp_path / "index.json"
    return AssetRegistry(db_path=str(db), json_index_path=str(js))


def test_queue_state_transitions():
    queue = OrchestratorQueue(checkpoint_file="cache/test_queue.json")
    queue.clear_checkpoint()

    # Job 2 depends on Job 1
    queue.add_job("job_1", {"job_id": "job_1", "generation_type": "text_to_image"})
    queue.add_job(
        "job_2",
        {"job_id": "job_2", "generation_type": "image_to_video"},
        deps=["job_1"],
    )

    assert queue.get_job("job_2")["status"] == QueueState.WAITING
    assert queue.get_runnable_jobs() == [queue.get_job("job_1")]

    # Finish job 1
    queue.update_job_status("job_1", QueueState.SUCCESS)
    assert queue.get_job("job_2")["status"] == QueueState.READY
    queue.clear_checkpoint()


@pytest.mark.asyncio
async def test_event_bus():
    bus = EventBus()
    called = []

    async def listener(event, data):
        called.append(data)

    bus.subscribe("TEST_EVENT", listener)
    await bus.emit("TEST_EVENT", "hello")
    assert called == ["hello"]


def test_asset_registry_db(clean_cache):
    job = {
        "prompt": "Krishna baby",
        "negative_prompt": "ugly",
        "references": [],
        "duration": 5,
        "resolution": "720p",
        "provider": "pixverse",
    }
    phash = clean_cache.generate_prompt_hash(job)
    assert phash is not None

    # SQLite check
    assert clean_cache.get_cached_asset(phash) is None

    # Register fake path
    fake_path = Path("fake_shot.mp4")
    # Touch fake path so it exists
    fake_path.touch()
    clean_cache.register_asset(phash, fake_path, job, {"created_at": "now"})

    assert clean_cache.get_cached_asset(phash) == "fake_shot.mp4"
    fake_path.unlink()


def test_budget_limits(tmp_path):
    budget_file = tmp_path / "budget.json"
    mgr = BudgetManager(budget_file=str(budget_file), daily_limit=20)

    assert mgr.check_budget_limit(10) is True
    mgr.deduct_credits(15)
    assert mgr.check_budget_limit(10) is False  # would exceed 20 limit


@pytest.mark.asyncio
async def test_executor_mocks(tmp_path):
    # Mock provider
    class MockProvider:
        async def generate_image(self, prompt):
            class Res:
                video_id = "v_123"

            return Res()

        async def get_task_status(self, vid):
            class Res:
                class Status:
                    name = "SUCCESS"

                status = Status()
                video_url = "http://test.com/out.mp4"
                error_message = None

            return Res()

        async def download_asset(self, **kwargs):
            return Path("out.png")

    executor = OrchestratorExecutor(provider=MockProvider())
    job = {
        "generation_type": "text_to_image",
        "prompt": "Test",
        "negative_prompt": "ugly",
        "duration": 5,
        "references": [],
        "output_path": "downloads/Episode001/Scene001/Shot001.png",
    }
    path = await executor.execute_job(job)
    assert path == Path("out.png")


@pytest.mark.asyncio
async def test_dashboard_api(tmp_path):
    queue = OrchestratorQueue(checkpoint_file=str(tmp_path / "q.json"))
    budget = BudgetManager(budget_file=str(tmp_path / "b.json"))
    engine = OrchestratorEngine(production=False)

    from orchestrator.monitor import start_dashboard

    server = start_dashboard(queue, budget, engine, port=8089)

    # Test HTTP client status retrieval
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://127.0.0.1:8089/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

        resp_q = await client.get("http://127.0.0.1:8089/queue")
        assert resp_q.status_code == 200

    server.shutdown()


def test_cli_endpoints(tmp_path):
    # status check
    res_status = runner.invoke(app, ["status"])
    assert "No active orchestrator queue" in res_status.stdout

    # cancel check
    res_cancel = runner.invoke(app, ["cancel"])
    assert "No active queue checkpoint" in res_cancel.stdout
