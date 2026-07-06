from pathlib import Path

from story.continuity import ContinuityEngine
from story.parser import parse_episode
from story.validator import validate_episode


def main():
    episode = parse_episode(Path("Episode001.json"))
    errors = validate_episode(episode)
    if errors:
        print("Validation errors:")
        for err in errors:
            print(f"- {err}")
    else:
        print("Episode schema validation passed!")

    continuity = ContinuityEngine()
    warnings = continuity.validate_continuity(episode)
    if warnings:
        print("Continuity warnings:")
        for warn in warnings:
            print(f"- {warn}")
    else:
        print("Continuity validation passed!")


if __name__ == "__main__":
    main()
