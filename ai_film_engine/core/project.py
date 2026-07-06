from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ProjectSettings(BaseModel):
    budget_limit: int = 500
    resolution: str = "1920x1080"
    aspect_ratio: str = "16:9"
    fps: int = 24
    video_codec: str = "libx264"
    audio_codec: str = "aac"


class ProjectSpec(BaseModel):
    name: str
    title: str
    template: str = "youtube_series"
    created_at: str = "2026-07-06T12:00:00Z"
    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class ProjectManager:
    def __init__(self, workspace_path: str = "workspace"):
        self.workspace_path = Path(workspace_path)
        self.projects_dir = self.workspace_path / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(
        self, name: str, template: str = "youtube_series"
    ) -> ProjectSpec:
        """Create a new project structure and default project.yaml spec."""
        proj_dir = self.projects_dir / name
        proj_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        subdirs = ["assets", "episodes", "storyboards", "renders", "reports"]
        for sd in subdirs:
            (proj_dir / sd).mkdir(parents=True, exist_ok=True)

        spec = ProjectSpec(
            name=name,
            title=name.capitalize() + " Project",
            template=template,
        )

        yaml_path = proj_dir / "project.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(spec.model_dump(), f, default_flow_style=False)

        return spec

    def list_projects(self) -> list[str]:
        """Return list of project names available in workspace."""
        if not self.projects_dir.exists():
            return []
        return [
            p.name
            for p in self.projects_dir.iterdir()
            if p.is_dir() and (p / "project.yaml").exists()
        ]

    def load_project(self, name: str) -> ProjectSpec | None:
        """Load and parse project.yaml settings spec."""
        proj_dir = self.projects_dir / name
        yaml_path = proj_dir / "project.yaml"
        if not yaml_path.exists():
            return None
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return ProjectSpec(**data)

    def delete_project(self, name: str) -> bool:
        """Remove project folders from workspace."""
        proj_dir = self.projects_dir / name
        if proj_dir.exists() and proj_dir.is_dir():
            import shutil

            shutil.rmtree(proj_dir)
            return True
        return False
