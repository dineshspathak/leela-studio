import json
from pathlib import Path

from ai_film_engine.generator.engine import GenerationEngine


def main():
    print("=== RUNNING GENERATION ENGINE DEMO ===")

    # Create mock episode
    episode = {
        "episode": "Krishna Janm",
        "scenes": [
            {
                "scene_id": "Scene1",
                "location": "Prison Cell",
                "shots": [
                    {
                        "shot_id": "Scene1_Shot1",
                        "prompt": "Vasudeva holding baby Krishna",
                        "references": [],
                    }
                ],
            }
        ],
    }

    ep_path = Path("workspace/projects/leela/episodes/episode001/episode.json")
    ep_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ep_path, "w", encoding="utf-8") as f:
        json.dump(episode, f, indent=2)

    engine = GenerationEngine(profile_name="cinematic")
    manifest = engine.run_generation(str(ep_path), dry_run=False)

    print("\n=== GENERATION MANIFEST RESOLVED ===")
    print(f"Profile: {manifest['quality_profile']}")
    print(f"Reused Assets: {len(manifest['reused_assets'])}")
    print(f"Planned Jobs: {len(manifest['planned_jobs'])}")
    print(f"Estimated Credits: {manifest['estimated_credits']}")


if __name__ == "__main__":
    main()
