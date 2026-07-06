import asyncio
import json
from pathlib import Path

import typer

from orchestrator.engine import OrchestratorEngine
from orchestrator.queue import OrchestratorQueue
from story.compiler import StoryCompiler
from story.continuity import ContinuityEngine
from story.parser import parse_episode
from story.validator import validate_episode
from timeline.scheduler import CostEstimator, ExecutionScheduler

app = typer.Typer(help="LEELA Studio Story Engine & Orchestrator CLI")

@app.command()
def compile(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode (prints estimates without writing plans)"),
    output_dir: str = typer.Option("output", "--output-dir", help="Directory to save execution outputs"),
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

@app.command()
def generate(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    force: bool = typer.Option(False, "--force", help="Force recreate all assets, ignoring cache"),
    production: bool = typer.Option(False, "--production", help="Enable budget, checkpoints, retries, and caching"),
    workers: int = typer.Option(2, "--workers", help="Max concurrent workers"),
):
    """Run generation orchestrator for compiled episode plan."""
    file_path = Path(file)
    if not file_path.exists():
        typer.echo(f"Error: File '{file}' not found.", err=True)
        raise typer.Exit(code=1)

    episode = parse_episode(file_path)
    compiler = StoryCompiler()
    plan = compiler.compile_episode(episode)
    graph = compiler.generate_execution_graph(plan)

    # Save output/ExecutionPlan.json
    out_path = Path("output")
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "ExecutionPlan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    with open(out_path / "ExecutionGraph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    engine = OrchestratorEngine(production=production)
    typer.echo(f"Starting orchestrator in {'PRODUCTION' if production else 'DEVELOPMENT'} mode...")
    asyncio.run(engine.run(max_workers=workers, force=force))

@app.command()
def resume(
    production: bool = typer.Option(True, "--production", help="Enable budget, checkpoints, retries, and caching"),
    workers: int = typer.Option(2, "--workers", help="Max concurrent workers"),
):
    """Resume execution from last checkpoint queue state."""
    engine = OrchestratorEngine(production=production)
    typer.echo("Resuming orchestrator from checkpoint...")
    asyncio.run(engine.run(max_workers=workers))

@app.command()
def cancel():
    """Cancel running active jobs and clear checkpoint."""
    queue = OrchestratorQueue()
    if queue.load_checkpoint():
        queue.clear_checkpoint()
        typer.echo("Active queue cancelled and checkpoint cleared.")
    else:
        typer.echo("No active queue checkpoint found to cancel.")

@app.command()
def status():
    """Display progress and status of generation queue."""
    queue = OrchestratorQueue()
    if queue.load_checkpoint():
        total = len(queue.jobs)
        completed = sum(1 for j in queue.jobs.values() if j["status"] == "SUCCESS")
        running = sum(1 for j in queue.jobs.values() if j["status"] == "RUNNING")
        failed = sum(1 for j in queue.jobs.values() if j["status"] == "FAILED")
        waiting = sum(1 for j in queue.jobs.values() if j["status"] == "WAITING")
        typer.echo("Queue Status:")
        typer.echo(f"  Total: {total} | Completed: {completed} | Running: {running} | Failed: {failed} | Waiting: {waiting}")
    else:
        typer.echo("No active orchestrator queue is currently running.")

if __name__ == "__main__":
    app()
