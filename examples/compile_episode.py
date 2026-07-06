import json
from pathlib import Path

from story.compiler import StoryCompiler
from story.parser import parse_episode


def main():
    episode = parse_episode(Path("Episode001.json"))
    compiler = StoryCompiler()
    plan = compiler.compile_episode(episode)
    print("Compiled Execution Plan:")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
