from pathlib import Path

from director.director import DirectorEngine
from story.parser import parse_episode


def main():
    episode = parse_episode(Path("Episode001.json"))
    director = DirectorEngine()
    result = director.process_episode(episode, budget_limit=20)
    print("Shotlist generation details:")
    for s in result["shots"]:
        print(
            f"- {s['job_id']}: {s['prompt']} => {s['provider_flow']} (Credits: {s['credits']})"
        )


if __name__ == "__main__":
    main()
