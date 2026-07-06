import json

import httpx
import pytest
import respx

from ai_film_engine.generator.dispatcher import AdaptiveScheduler, ProviderHealthManager
from ai_film_engine.generator.engine import GenerationEngine
from ai_film_engine.generator.planner import UniversalPlanner
from ai_film_engine.generator.resolver import AssetResolver, MatchResult
from ai_film_engine.generator.tracker import AssetLineage, GenerationTracker


@pytest.fixture
def sample_episode_data(tmp_path):
    ep = {
        "episode": "Test Episode",
        "scenes": [
            {
                "scene_id": "Scene1",
                "location": "Gokul",
                "shots": [
                    {
                        "shot_id": "Scene1_Shot1",
                        "prompt": "Baby Krishna crawling",
                        "references": ["ref1.png"],
                    },
                    {
                        "shot_id": "Scene1_Shot2",
                        "prompt": "Devaki looking down sadly",
                        "references": [],
                    },
                ],
            }
        ],
    }
    ep_file = tmp_path / "Episode001.json"
    with open(ep_file, "w", encoding="utf-8") as f:
        json.dump(ep, f)
    return ep_file


def test_asset_resolver():
    resolver = AssetResolver()
    h = resolver.calculate_prompt_hash("hello")
    assert isinstance(h, str)

    registry = [
        {"prompt_hash": resolver.calculate_prompt_hash("hello"), "path": "matched.png"},
        {"prompt": "hello word", "path": "similar.png", "resolution": "1280x720"},
    ]

    res = resolver.resolve_asset_matching(
        prompt="hello",
        neg_prompt="",
        references=[],
        metadata={"resolution": "1280x720", "duration": 4.0, "provider": "pixverse"},
        registry_assets=registry,
    )
    assert res.matched is True
    assert res.match_level == "exact_hash"
    assert res.asset_path == "matched.png"


def test_tracker():
    tracker = GenerationTracker()
    tracker.update_status("job1", "RUNNING")
    assert tracker.get_status("job1") == "RUNNING"

    lin = AssetLineage(
        asset_id="asset1",
        provider="pixverse",
        model="v1",
        workflow="draft",
        episode="ep",
        scene="sc",
        shot="sh",
    )
    tracker.register_lineage("asset1", lin)
    assert tracker.lineages["asset1"].provider == "pixverse"


def test_planner_and_health():
    planner = UniversalPlanner(profile_name="draft")
    hm = ProviderHealthManager()
    scheduler = AdaptiveScheduler(hm)

    episode = {
        "scenes": [{"shots": [{"shot_id": "Shot1", "prompt": "p1", "references": []}]}]
    }

    resolved = {"Shot1": MatchResult(matched=False, confidence=0.0, match_level="none")}

    # Test health check
    health = hm.check_health()
    assert "pixverse" in health

    manifest = planner.plan_generation(episode, resolved, health)
    assert manifest["quality_profile"] == "draft"

    # Test rebalancing of unhealthy provider jobs
    jobs = [{"job_id": "job1", "provider": "runway"}]
    rebalanced = scheduler.schedule_jobs(jobs)
    assert rebalanced[0]["provider"] == "pixverse"


@respx.mock
def test_generation_engine(sample_episode_data, tmp_path, monkeypatch):
    monkeypatch.setenv("PIXVERSE_API_KEY", "mock_key")
    respx.get("https://app-api.pixverse.ai/openapi/v2/account/balance").mock(
        return_value=httpx.Response(200, json={"code": 0, "msg": "success"})
    )

    # Set up active registry database mock
    reg_file = tmp_path / "cache/asset_registry.json"
    reg_file.parent.mkdir(parents=True, exist_ok=True)
    with open(reg_file, "w", encoding="utf-8") as f:
        f.write("[]")

    engine = GenerationEngine(workspace_path=str(tmp_path), profile_name="draft")
    manifest = engine.run_generation(str(sample_episode_data), dry_run=False)
    assert manifest["quality_profile"] == "draft"

    # Verify manifest & report files created
    assert (tmp_path / "projects/Test Episode/generation_manifest.json").exists()
    assert (
        tmp_path / "projects/Test Episode/reports/production_analytics.json"
    ).exists()
