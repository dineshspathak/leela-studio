from pathlib import Path

from director.director import DirectorEngine
from story.parser import parse_episode


def main():
    episode = parse_episode(Path("Episode001.json"))
    director = DirectorEngine()
    result = director.process_episode(episode, budget_limit=15)
    print("Storyboard complete! Re-design parameters output:")
    for s in result["shots"]:
        print(
            f"Shot: {s['job_id']} | "
            f"Framing: {s['framing']} | "
            f"Lighting: {s['lighting']} | "
            f"Emotion: {s['emotion']}"
        )


if __name__ == "__main__":
    main()
