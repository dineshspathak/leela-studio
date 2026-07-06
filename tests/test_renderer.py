import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from main import app
from renderer.audio import AudioEngine
from renderer.engine import MovieRendererEngine
from renderer.ffmpeg import FFmpegCommandCompiler
from renderer.plugins.bloom import BloomPlugin
from renderer.plugins.grain import GrainPlugin
from renderer.plugins.kenburns import KenBurnsPlugin
from renderer.scene_graph import Clip, EffectPlugin, SceneGraph, Track
from renderer.subtitles import SubtitleEngine
from renderer.transitions.crossfade import CrossfadeTransition
from story.parser import parse_episode

runner = CliRunner()


@pytest.fixture
def sample_episode_json(tmp_path):
    data = {
        "episode_id": "1",
        "title": "Krishna Birth Story",
        "variables": {},
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
        "characters": [],
        "locations": [],
        "scenes": [
            {
                "scene_id": "1",
                "title": "Scene 1",
                "shots": [
                    {
                        "shot_id": "1",
                        "title": "Shot 1",
                        "generation_type": "text_to_image",
                        "prompt": "Devaki sitting",
                        "output_filename": "Shot001.png",
                    }
                ],
            }
        ],
    }
    file_path = tmp_path / "Episode001.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return file_path


def test_scene_graph():
    graph = SceneGraph(scene_id="Scene1")
    track = Track(track_id="V1", track_type="video")
    clip = Clip(
        clip_id="Clip1",
        start_time=0.0,
        end_time=5.0,
        asset_path="assets/img.png",
        effects=[EffectPlugin(name="grain", params={"intensity": 3})],
    )
    track.clips.append(clip)
    graph.tracks.append(track)

    assert graph.scene_id == "Scene1"
    assert graph.tracks[0].clips[0].effects[0].name == "grain"


def test_subtitle_engine(tmp_path):
    engine = SubtitleEngine()
    clips = [{"start_time": 0.0, "end_time": 5.0, "text": "Testing Subtitles"}]
    base = tmp_path / "sub"
    paths = engine.build_subtitle_files(clips, str(base))

    assert Path(paths["srt"]).exists()
    assert Path(paths["ass"]).exists()


def test_audio_engine():
    engine = AudioEngine()
    snippet = engine.mix_tracks("narr.mp3", "music.mp3")
    assert "sidechaincompress" in snippet
    assert "amix" in snippet


def test_ffmpeg_command_compiler():
    compiler = FFmpegCommandCompiler()
    graph = {
        "inputs": [{"id": 0, "path": "in.mp4"}],
        "filters": [{"expr": "[0:v]hflip[outv]"}],
        "outputs": [
            {"map": "outv", "codec": "libx264", "bitrate": "8M", "path": "out.mp4"}
        ],
    }
    cmd = compiler.compile_graph_to_command(graph)
    assert "-i in.mp4" in cmd
    assert "hflip" in cmd
    assert "-c:v libx264" in cmd


def test_effect_plugins():
    grain = GrainPlugin()
    res = grain.render_filter("in", "out", {"intensity": 10})
    assert "noise=alls=10" in res

    bloom = BloomPlugin()
    res = bloom.render_filter("in", "out", {"radius": 5})
    assert "gblur" in res

    kb = KenBurnsPlugin()
    res = kb.render_filter("in", "out", {"direction": "push_in"})
    assert "zoompan" in res


def test_transition_plugins():
    xfade = CrossfadeTransition()
    res = xfade.render_transition("a", "b", "out", 4.5, 0.5)
    assert "xfade" in res
    assert "offset=4.5" in res


def test_renderer_engine(sample_episode_json, tmp_path):
    episode = parse_episode(sample_episode_json)
    from story.compiler import StoryCompiler

    plan = StoryCompiler().compile_episode(episode)

    engine = MovieRendererEngine(
        cache_dir=str(tmp_path / "cache"), report_path=str(tmp_path / "report.json")
    )
    out_video = engine.render_episode(episode.title, plan)

    assert out_video.exists()
    assert Path(f"{episode.title}.manifest.json").exists()
    assert Path(f"{episode.title}.srt").exists()
    assert Path(f"{episode.title}.ass").exists()
    assert (tmp_path / "report.json").exists()

    # Cleanup files
    Path(f"{episode.title}.manifest.json").unlink()
    Path(f"{episode.title}.srt").unlink()
    Path(f"{episode.title}.ass").unlink()
    Path(f"{episode.title}.mp4").unlink()


def test_cli_rendering(sample_episode_json):
    res_render = runner.invoke(app, ["render", str(sample_episode_json)])
    assert res_render.exit_code == 0
    assert "render complete" in res_render.stdout.lower()

    res_preview = runner.invoke(app, ["preview", str(sample_episode_json)])
    assert res_preview.exit_code == 0
    assert "preview render complete" in res_preview.stdout.lower()

    res_make = runner.invoke(app, ["make", str(sample_episode_json)])
    assert res_make.exit_code == 0
    assert "production pipeline completed" in res_make.stdout.lower()

    # Cleanup created artifacts
    Path("Krishna Birth Story.mp4").unlink()
    Path("Krishna Birth Story.manifest.json").unlink()
    Path("Krishna Birth Story.srt").unlink()
    Path("Krishna Birth Story.ass").unlink()
