import asyncio
import json
from pathlib import Path

import typer

from ai_film_engine.core.project import ProjectManager
from ai_film_engine.director.compiler import StoryCompiler
from ai_film_engine.director.continuity import ContinuityEngine
from ai_film_engine.director.parser import parse_episode
from ai_film_engine.director.validator import validate_episode
from ai_film_engine.orchestrator.engine import OrchestratorEngine
from ai_film_engine.orchestrator.queue import OrchestratorQueue
from ai_film_engine.renderer.engine import MovieRendererEngine
from ai_film_engine.timeline.scheduler import CostEstimator, ExecutionScheduler

app = typer.Typer(help="AI Film Engine Filmmaking Platform CLI")
project_app = typer.Typer(help="Manage filmmaking projects")
app.add_typer(project_app, name="project")


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

        typer.echo("\n--- Cost & Resource Estimates ---")
        typer.echo(f"  Estimated Images: {costs['estimated_images']}")
        typer.echo(f"  Estimated Image-to-Video: {costs['estimated_image_to_video']}")
        typer.echo(f"  Estimated Text-to-Video: {costs['estimated_text_to_video']}")
        typer.echo(f"  Total Estimated Credits: {costs['total_estimated_credits']}")
        typer.echo(f"  Estimated Runtime: {costs['estimated_runtime_seconds']} seconds")
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
def storyboard(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    budget: int = typer.Option(15, "--budget", help="Target episode budget limits"),
):
    """Generate professional film storyboards from Episode Story DSL."""
    file_path = Path(file)
    if not file_path.exists():
        typer.echo(f"Error: File '{file}' not found.", err=True)
        raise typer.Exit(code=1)

    typer.echo("Invoking LEELA Director AI...")
    from ai_film_engine.director.director import DirectorEngine

    episode = parse_episode(file_path)
    director = DirectorEngine()
    director.process_episode(episode, budget_limit=budget)

    typer.echo("✅ Storyboard generation completed!")
    typer.echo("Generated outputs:")
    typer.echo("  - output/Storyboard.json")
    typer.echo("  - output/Storyboard.md")
    typer.echo("  - output/Storyboard.pdf")
    typer.echo("  - reports/continuity_report.md")
    typer.echo("  - director_notes.md")
    typer.echo("  - production_notes.md")


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
    force: bool = typer.Option(
        False, "--force", help="Force recreate all assets, ignoring cache"
    ),
    production: bool = typer.Option(
        False, "--production", help="Enable budget, checkpoints, retries, and caching"
    ),
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
    typer.echo(
        f"Starting orchestrator in {'PRODUCTION' if production else 'DEVELOPMENT'} mode..."
    )
    asyncio.run(engine.run(max_workers=workers, force=force))


@app.command()
def resume(
    production: bool = typer.Option(
        True, "--production", help="Enable budget, checkpoints, retries, and caching"
    ),
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
        typer.echo(
            f"  Total: {total} | Completed: {completed} | Running: {running} | Failed: {failed} | Waiting: {waiting}"
        )
    else:
        typer.echo("No active orchestrator queue is currently running.")


@app.command()
def render(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    profile: str = typer.Option(
        "youtube",
        "--profile",
        help="Export profile name (youtube, shorts, instagram, master)",
    ),
):
    """Render the full final movie from compiled episode plan and storyboard."""
    file_path = Path(file)
    if not file_path.exists():
        typer.echo(f"Error: File '{file}' not found.", err=True)
        raise typer.Exit(code=1)

    typer.echo("Compiling story and loading assets...")
    episode = parse_episode(file_path)
    compiler = StoryCompiler()
    plan = compiler.compile_episode(episode)

    renderer_engine = MovieRendererEngine()

    typer.echo("Running movie rendering engine...")
    out_path = renderer_engine.render_episode(episode.title, plan, profile_name=profile)
    typer.echo(f"✅ Render complete! Output video: {out_path}")


@app.command()
def preview(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
):
    """Render a 30-second preview of the episode."""
    file_path = Path(file)
    if not file_path.exists():
        typer.echo(f"Error: File '{file}' not found.", err=True)
        raise typer.Exit(code=1)

    episode = parse_episode(file_path)
    compiler = StoryCompiler()
    plan = compiler.compile_episode(episode)

    renderer_engine = MovieRendererEngine()

    typer.echo("Rendering preview clips...")
    out_path = renderer_engine.render_episode(episode.title, plan, preview=True)
    typer.echo(f"✅ Preview render complete! Output video: {out_path}")


@app.command()
def export(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    profile: str = typer.Option(
        ...,
        "--profile",
        help="Export profile name (youtube, shorts, instagram, master)",
    ),
):
    """Export the movie applying specific profile settings."""
    render(file, profile)


@app.command()
def make(
    file: str = typer.Argument(..., help="Path to Episode JSON file"),
    profile: str = typer.Option("youtube", "--profile", help="Export profile name"),
    budget: int = typer.Option(15, "--budget", help="Target credits budget limit"),
):
    """One-Command Build: Parse, validate, compile storyboard, orchestrate, and render finished movie!"""
    typer.echo("=== STARTING FULL PRODUCTION PIPELINE ===")
    storyboard(file, budget=budget)
    generate(file, force=False, production=False, workers=2)
    render(file, profile=profile)
    typer.echo("=== PRODUCTION PIPELINE COMPLETED SUCCESSFULLY ===")


# Project Sub-Commands
@project_app.command(name="list")
def project_list():
    """List all registered filmmaking projects."""
    mgr = ProjectManager()
    projects = mgr.list_projects()
    if not projects:
        typer.echo("No projects found in workspace.")
    else:
        typer.echo("Registered Projects:")
        for p in projects:
            typer.echo(f"  - {p}")


@project_app.command(name="create")
def project_create(
    name: str = typer.Argument(..., help="Name of the project"),
    template: str = typer.Option(
        "youtube_series", "--template", help="Project template name"
    ),
):
    """Create a new filmmaking project workspace."""
    mgr = ProjectManager()
    spec = mgr.create_project(name, template=template)
    typer.echo(
        f"✅ Created project '{spec.name}' from template '{spec.template}' successfully!"
    )


@project_app.command(name="open")
def project_open(name: str = typer.Argument(..., help="Name of the project")):
    """Open and load project configuration details."""
    mgr = ProjectManager()
    spec = mgr.load_project(name)
    if not spec:
        typer.echo(f"Error: Project '{name}' not found.", err=True)
    else:
        typer.echo(f"Opened Project: {spec.title}")
        typer.echo(f"  Template: {spec.template}")
        typer.echo(f"  Resolution: {spec.settings.resolution}")


@project_app.command(name="delete")
def project_delete(name: str = typer.Argument(..., help="Name of the project")):
    """Delete a filmmaking project from the workspace."""
    mgr = ProjectManager()
    if mgr.delete_project(name):
        typer.echo(f"✅ Deleted project '{name}' successfully.")
    else:
        typer.echo(f"Error: Project '{name}' not found.", err=True)


@project_app.command(name="build")
def project_build(
    name: str = typer.Argument(..., help="Project name"),
    episode_id: str = typer.Argument(..., help="Episode ID to build"),
):
    """Parse, compile, orchestrate, and render movie for specified project episode."""
    mgr = ProjectManager()
    spec = mgr.load_project(name)
    if not spec:
        typer.echo(f"Error: Project '{name}' not found.", err=True)
        raise typer.Exit(code=1)

    ep_path = (
        Path("workspace/projects")
        / name
        / "episodes"
        / f"episode{episode_id}"
        / "episode.json"
    )
    if not ep_path.exists():
        ep_path = Path("workspace/projects") / name / "episode.json"

    if not ep_path.exists():
        typer.echo(f"Error: Episode path '{ep_path}' not found.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Building {name} episode {episode_id}...")
    make(str(ep_path), profile="youtube", budget=spec.settings.budget_limit)
    typer.echo("✅ Project build complete!")


if __name__ == "__main__":
    app()
