import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_film_engine.director.camera import CameraEngine
from ai_film_engine.director.composition import CompositionEngine
from ai_film_engine.director.continuity import QualityChecker
from ai_film_engine.director.director import DirectorEngine
from ai_film_engine.director.emotions import EmotionsEngine
from ai_film_engine.director.language import CinematicLanguageEngine
from ai_film_engine.director.lighting import LightingEngine
from ai_film_engine.director.motion import MotionEngine
from ai_film_engine.director.parser import parse_episode
from ai_film_engine.director.state import StateEngine
from ai_film_engine.director.storyboard import StoryboardBuilder
from main import app

runner = CliRunner()


@pytest.fixture
def sample_episode_json(tmp_path):
    data = {
        "episode_id": "1",
        "title": "Krishna Birth Story",
        "variables": {"hero": "Krishna"},
        "global_defaults": {
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "fps": 24,
            "provider": "pixverse",
            "camera_style": "static",
            "visual_style": "3D render",
            "cinematic_profile": "volumetric lighting",
            "negative_prompt": "blurry",
        },
        "characters": [
            {"name": "Devaki", "description": "mother", "costume": "red saree"}
        ],
        "locations": [{"name": "Prison", "environment": "dungeon"}],
        "scenes": [
            {
                "scene_id": "1",
                "title": "Scene 1",
                "location": "Prison",
                "shots": [
                    {
                        "shot_id": "1",
                        "title": "Shot 1",
                        "generation_type": "text_to_image",
                        "prompt": "Devaki sitting",
                        "characters": ["Devaki"],
                    },
                    {
                        "shot_id": "2",
                        "title": "Shot 2",
                        "generation_type": "image_to_video",
                        "prompt": "Devaki crying",
                        "characters": ["Devaki"],
                        "references": ["Scene1_Shot1"],
                    },
                ],
            }
        ],
    }
    file_path = tmp_path / "Episode001.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file_path


def test_language_formatting():
    engine = CinematicLanguageEngine()
    formatted = engine.format_shot_description(
        framing="close up",
        movement="push in",
        lighting="golden hour",
        composition="center",
        motion="breathing",
        emotion="sadness",
    )
    assert "85mm portrait lens" in formatted
    assert "push-in" in formatted
    assert "sunset golden hour" in formatted


def test_state_continuity():
    engine = StateEngine()
    engine.register_character("Devaki", costume="red saree")

    shot_info = {
        "shot_id": "1",
        "characters": ["Devaki"],
        "character_updates": {"Devaki": {"costume": "blue saree"}},
    }
    warnings = engine.transition_state(shot_info)
    assert any("Costume for 'Devaki' changed" in w for w in warnings)


def test_sub_engines():
    camera = CameraEngine()
    setup = camera.recommend_setup(importance="HERO", is_action=True)
    assert setup["framing"] == "low angle"

    lighting = LightingEngine()
    light = lighting.recommend_lighting("night", "indoor")
    assert light == "torch"

    emotions = EmotionsEngine()
    emotion = emotions.recommend_emotion("Devaki weeping in dungeon")
    assert emotion == "sadness"

    composition = CompositionEngine()
    comp = composition.recommend_composition("close up")
    assert comp == "center"

    motion = MotionEngine()
    mot = motion.recommend_motion("close up")
    assert "breathing" in mot


def test_quality_checker():
    checker = QualityChecker(report_path="cache/test_report.md")
    shots = [
        {
            "job_id": "Shot_1",
            "framing": "close up",
            "movement": "static",
            "lighting": "soft",
            "emotion": "hope",
        },
        {
            "job_id": "Shot_2",
            "framing": "close up",
            "movement": "static",
            "lighting": "soft",
            "emotion": "hope",
        },
        {
            "job_id": "Shot_3",
            "framing": "close up",
            "movement": "static",
            "lighting": "soft",
            "emotion": "hope",
        },
    ]
    warnings = checker.verify_episode_continuity(shots)
    assert any("Camera framing 'close up' repeated" in w for w in warnings)
    assert any("Camera movement 'static' repeated" in w for w in warnings)

    report = Path("cache/test_report.md")
    assert report.exists()
    report.unlink()


def test_storyboard_builder(tmp_path):
    builder = StoryboardBuilder(output_dir=str(tmp_path))
    shots = [
        {
            "job_id": "Scene1_Shot1",
            "framing": "close up",
            "movement": "push in",
            "lighting": "moonlight",
            "composition": "center",
            "motion": "breathing",
            "emotion": "sadness",
            "credits": 10,
            "cinematic_prompt": "Cinematic prompt 1",
        }
    ]
    builder.build_storyboard_files("Test Episode", shots)

    assert (tmp_path / "Storyboard.json").exists()
    assert (tmp_path / "Storyboard.md").exists()
    assert (tmp_path / "Storyboard.pdf").exists()


def test_director_optimizer(sample_episode_json, tmp_path):
    episode = parse_episode(sample_episode_json)
    director = DirectorEngine()

    # Process with tight budget to trigger optimizer
    result = director.process_episode(episode, budget_limit=11)

    # Check if budget optimization occurred
    total_credits = sum(s["credits"] for s in result["shots"])
    assert total_credits <= 11

    # Check notes generated
    assert Path("director_notes.md").exists()
    assert Path("production_notes.md").exists()
    Path("director_notes.md").unlink()
    Path("production_notes.md").unlink()


def test_cli_storyboard(sample_episode_json):
    result = runner.invoke(
        app, ["storyboard", str(sample_episode_json), "--budget", "15"]
    )
    assert result.exit_code == 0
    assert "storyboard generation completed" in result.stdout.lower()
