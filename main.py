import json
from pathlib import Path

import typer

from story.compiler import StoryCompiler
from story.continuity import ContinuityEngine
from story.parser import parse_episode
from story.validator import validate_episode
from timeline.scheduler import CostEstimator, ExecutionScheduler

app = typer.Typer(help="LEELA Studio Story Engine CLI")


@app.command()
def compile(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Dry run mode (prints estimates without writing plans)"
    ),
    output_dir: str = typer.Option(
        "output", "--output-dir", help="Directory to save execution outputs"
    ),
):
    """Compile an Episode Story DSL JSON into ExecutionPlan and ExecutionGraph."""
    file_path = Path(file)
    if not file_path.exists():
        typer.echo(f"Error: File '{file}' not found.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Parsing episode: {file}...")
    episode = parse_episode(file_path)

    # 1. Validation
    typer.echo("Validating episode rules...")
    errors = validate_episode(episode)
    if errors:
        typer.echo("❌ Validation errors found:")
        for err in errors:
            typer.echo(f"  - {err}")
        raise typer.Exit(code=1)
    typer.echo("✅ Validation successful!")

    # 2. Continuity check
    typer.echo("Running visual continuity engine...")
    continuity_engine = ContinuityEngine()
    warnings = continuity_engine.validate_continuity(episode)
    if warnings:
        typer.echo("⚠️ Continuity warnings found:")
        for warn in warnings:
            typer.echo(f"  - {warn}")
    else:
        typer.echo("✅ Continuity checks passed!")

    # 3. Compilation
    typer.echo("Compiling story to execution plan...")
    compiler = StoryCompiler()
    plan = compiler.compile_episode(episode)
    graph = compiler.generate_execution_graph(plan)

    # Cost estimation
    estimator = CostEstimator()
    costs = estimator.estimate_costs(plan)

    # Scheduling order
    scheduler = ExecutionScheduler()
    order = scheduler.schedule_jobs(plan, graph)

    if dry_run:
        typer.echo("\n=== DRY RUN MODE ===")
        typer.echo(f"Episode: {plan['title']}")
        typer.echo(f"Execution Order: {order}")
        typer.echo("--- Resolved Jobs ---")
        for job in plan["jobs"]:
            typer.echo(f"Job: {job['job_id']}")
            typer.echo(f"  Prompt: {job['prompt']}")
            typer.echo(f"  References: {job['references']}")
            typer.echo(f"  Output Path: {job['output_path']}")

        typer.echo("\n--- Cost & Resource Estimates ---")
        typer.echo(f"  Estimated Images: {costs['estimated_images']}")
        typer.echo(f"  Estimated Image-to-Video: {costs['estimated_image_to_video']}")
        typer.echo(f"  Estimated Text-to-Video: {costs['estimated_text_to_video']}")
        typer.echo(f"  Total Estimated Credits: {costs['total_estimated_credits']}")
        typer.echo(f"  Estimated Runtime: {costs['estimated_runtime_seconds']} seconds")
        typer.echo("=====================")
    else:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        plan_file = out_path / "ExecutionPlan.json"
        graph_file = out_path / "ExecutionGraph.json"

        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
        with open(graph_file, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)

        typer.echo(f"\nSaved execution files successfully to {out_path}/")
        typer.echo(f"  Plan: {plan_file}")
        typer.echo(f"  Graph: {graph_file}")


@app.command()
def validate(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
):
    """Validate an Episode Story DSL JSON for logic and continuity."""
    file_path = Path(file)
    if not file_path.exists():
        typer.echo(f"Error: File '{file}' not found.", err=True)
        raise typer.Exit(code=1)

    episode = parse_episode(file_path)
    errors = validate_episode(episode)
    if errors:
        typer.echo("❌ Validation errors found:")
        for err in errors:
            typer.echo(f"  - {err}")
        raise typer.Exit(code=1)

    continuity_engine = ContinuityEngine()
    warnings = continuity_engine.validate_continuity(episode)
    if warnings:
        typer.echo("⚠️ Continuity warnings found:")
        for warn in warnings:
            typer.echo(f"  - {warn}")
    else:
        typer.echo("✅ All validation and continuity checks passed successfully!")


if __name__ == "__main__":
    app()
