import json
from pathlib import Path

from story.compiler import StoryCompiler
from story.parser import parse_episode
from timeline.scheduler import CostEstimator, ExecutionScheduler


def main():
    episode = parse_episode(Path("Episode001.json"))
    compiler = StoryCompiler()
    plan = compiler.compile_episode(episode)
    graph = compiler.generate_execution_graph(plan)

    estimator = CostEstimator()
    costs = estimator.estimate_costs(plan)

    scheduler = ExecutionScheduler()
    order = scheduler.schedule_jobs(plan, graph)

    print("Execution Plan:")
    print(json.dumps(plan, indent=2))
    print("\nExecution Graph:")
    print(json.dumps(graph, indent=2))
    print("\nCost Estimates:")
    print(json.dumps(costs, indent=2))
    print("\nExecution Order:")
    print(order)


if __name__ == "__main__":
    main()
