import json

import pytest
from typer.testing import CliRunner

from episodes.schemas import Episode, GlobalDefaults, Shot
from main import app
from story.asset_resolver import AssetResolver
from story.compiler import StoryCompiler
from story.continuity import ContinuityEngine
from story.parser import parse_episode, substitute_variables
from story.prompts import PromptBuilder
from story.validator import validate_episode
from timeline.builder import TimelineBuilder
from timeline.scheduler import CostEstimator, ExecutionScheduler

runner = CliRunner()


@pytest.fixture
def sample_episode_json(tmp_path):
    data = {
        "episode_id": "1",
        "title": "Test Episode",
        "variables": {"hero": "Krishna", "prison": "Kamsa Dungeon"},
        "global_defaults": {
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "fps": 24,
            "provider": "pixverse",
            "camera_style": "static",
            "visual_style": "3D render",
            "cinematic_profile": "dramatic lighting",
            "negative_prompt": "blurry, low quality",
        },
        "characters": [
            {
                "name": "Krishna",
                "description": "Divine child",
                "costume": "yellow pitambara",
                "master_asset_id": "char_krishna",
            }
        ],
        "locations": [
            {
                "name": "Kamsa Dungeon",
                "environment": "indoor",
                "lighting_default": "torches",
                "master_asset_id": "loc_prison",
            }
        ],
        "scenes": [
            {
                "scene_id": "1",
                "title": "Scene One",
                "location": "${prison}",
                "camera_default": "pan",
                "lighting_default": "dark",
                "provider_default": "pixverse",
                "shots": [
                    {
                        "shot_id": "1",
                        "title": "Shot One",
                        "generation_type": "text_to_image",
                        "prompt": "${hero} standing in dungeon",
                        "camera": "wide shot",
                        "characters": ["Krishna"],
                        "output_filename": "Shot001.png",
                    },
                    {
                        "shot_id": "2",
                        "title": "Shot Two",
                        "generation_type": "image_to_video",
                        "prompt": "${hero} smiles",
                        "camera": "close up",
                        "references": ["Scene1_Shot1"],
                        "characters": ["Krishna"],
                        "output_filename": "Shot002.mp4",
                    },
                ],
            }
        ],
    }
    file_path = tmp_path / "Episode001.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file_path


def test_variable_substitution():
    text = "Hello $hero in ${prison}!"
    vars_dict = {"hero": "Krishna", "prison": "Kamsa Dungeon"}
    substituted = substitute_variables(text, vars_dict)
    assert substituted == "Hello Krishna in Kamsa Dungeon!"


def test_parser(sample_episode_json):
    episode = parse_episode(sample_episode_json)
    assert episode.episode_id == "1"
    assert episode.scenes[0].location == "Kamsa Dungeon"
    assert episode.scenes[0].shots[0].prompt == "Krishna standing in dungeon"


def test_asset_resolver(tmp_path):
    resolver = AssetResolver(base_dir=str(tmp_path))
    char_path = resolver.resolve_character_asset("Devaki")
    assert char_path.name == "master.png"
    assert char_path.parent.name == "devaki"

    loc_path = resolver.resolve_location_asset("Kamsa Prison")
    assert loc_path.name == "master.png"
    assert loc_path.parent.name == "kamsa_prison"


def test_prompt_builder():
    builder = PromptBuilder(templates_dir="prompt_templates")
    defaults = GlobalDefaults()
    shot = Shot(
        shot_id="1",
        title="Test Shot",
        generation_type="text_to_image",
        prompt="Baby Krishna crawling",
        location="Gokul",
        camera="medium shot",
    )
    prompt = builder.build_prompt(shot, defaults)
    assert "Baby Krishna crawling in Gokul" in prompt
    assert "medium shot" in prompt


def test_validator():
    episode = Episode(
        episode_id="1",
        title="Test",
        scenes=[
            {
                "scene_id": "1",
                "title": "Scene 1",
                "shots": [
                    {
                        "shot_id": "1",
                        "title": "Shot 1",
                        "generation_type": "text_to_image",
                        "prompt": "",  # Invalid empty prompt
                        "duration": -5,  # Invalid duration
                    }
                ],
            }
        ],
    )
    errors = validate_episode(episode)
    assert any("missing a prompt" in err for err in errors)
    assert any("invalid duration" in err for err in errors)


def test_continuity_checks():
    episode = Episode(
        episode_id="1",
        title="Test",
        scenes=[
            {
                "scene_id": "1",
                "title": "Scene 1",
                "shots": [
                    {
                        "shot_id": "1",
                        "title": "Shot 1",
                        "generation_type": "text_to_image",
                        "prompt": "Devaki weeping",
                        "characters": ["Devaki"],  # Undefined character
                    }
                ],
            }
        ],
    )
    engine = ContinuityEngine()
    warnings = engine.validate_continuity(episode)
    assert any(
        "is not defined in the Episode's character registry" in w for w in warnings
    )


def test_compiler_and_graph(sample_episode_json):
    episode = parse_episode(sample_episode_json)
    compiler = StoryCompiler(templates_dir="prompt_templates")
    plan = compiler.compile_episode(episode)
    graph = compiler.generate_execution_graph(plan)

    assert plan["episode_id"] == "1"
    assert len(plan["jobs"]) == 2
    assert plan["jobs"][0]["job_id"] == "Scene1_Shot1"
    assert graph["nodes"] == ["Scene1_Shot1", "Scene1_Shot2"]
    assert graph["edges"] == [{"from": "Scene1_Shot1", "to": "Scene1_Shot2"}]


def test_timeline_builder():
    plan = {
        "episode_id": "1",
        "title": "Test",
        "jobs": [
            {
                "job_id": "Scene1_Shot1",
                "duration": 5,
                "prompt": "prompt 1",
                "output_path": "out1.png",
            },
            {
                "job_id": "Scene1_Shot2",
                "duration": 8,
                "prompt": "prompt 2",
                "output_path": "out2.mp4",
            },
        ],
    }
    builder = TimelineBuilder()
    timeline = builder.build_timeline(plan)
    assert timeline["total_duration"] == 13.0
    assert timeline["timeline"][1]["start_time"] == 5.0


def test_scheduler_and_estimator():
    plan = {
        "episode_id": "1",
        "title": "Test",
        "jobs": [
            {"job_id": "Scene1_Shot1", "generation_type": "text_to_image"},
            {"job_id": "Scene1_Shot2", "generation_type": "image_to_video"},
        ],
    }
    graph = {
        "nodes": ["Scene1_Shot1", "Scene1_Shot2"],
        "edges": [{"from": "Scene1_Shot1", "to": "Scene1_Shot2"}],
    }

    scheduler = ExecutionScheduler()
    order = scheduler.schedule_jobs(plan, graph)
    assert order == ["Scene1_Shot1", "Scene1_Shot2"]

    estimator = CostEstimator()
    costs = estimator.estimate_costs(plan)
    assert costs["estimated_images"] == 1
    assert costs["estimated_image_to_video"] == 1
    assert costs["total_estimated_credits"] == 11


def test_cli_compile(sample_episode_json, tmp_path):
    output_dir = tmp_path / "out"
    result = runner.invoke(
        app, ["compile", str(sample_episode_json), "--output-dir", str(output_dir)]
    )
    assert result.exit_code == 0
    assert (output_dir / "ExecutionPlan.json").exists()
    assert (output_dir / "ExecutionGraph.json").exists()


def test_cli_dry_run(sample_episode_json):
    result = runner.invoke(app, ["compile", str(sample_episode_json), "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.stdout
    assert "Cost & Resource Estimates" in result.stdout
