from typing import Any

from episodes.schemas import Episode
from story.asset_resolver import AssetResolver
from story.prompts import PromptBuilder


class StoryCompiler:
    def __init__(
        self, templates_dir: str = "prompt_templates", assets_dir: str = "assets"
    ):
        self.resolver = AssetResolver(assets_dir)
        self.prompt_builder = PromptBuilder(templates_dir)

    def compile_episode(self, episode: Episode) -> dict[str, Any]:
        """Compile an Episode object into a provider-agnostic ExecutionPlan."""
        jobs: list[dict[str, Any]] = []
        defaults = episode.global_defaults

        for scene in episode.scenes:
            scene_loc = scene.location
            scene_camera = scene.camera_default
            scene_lighting = scene.lighting_default
            scene_duration = scene.duration_default
            scene_provider = scene.provider_default
            scene_negative_prompt = scene.negative_prompt_default

            for shot in scene.shots:
                # 1. Inherit defaults
                resolved_location = shot.location or scene_loc
                resolved_camera = shot.camera or scene_camera or defaults.camera_style
                resolved_motion = shot.motion or defaults.camera_style
                resolved_negative_prompt = (
                    shot.negative_prompt
                    or scene_negative_prompt
                    or defaults.negative_prompt
                )
                resolved_provider = shot.provider or scene_provider or defaults.provider
                resolved_duration = shot.duration or scene_duration or 5

                resolved_shot = shot.model_copy(
                    update={
                        "location": resolved_location,
                        "camera": resolved_camera,
                        "motion": resolved_motion,
                        "negative_prompt": resolved_negative_prompt,
                        "provider": resolved_provider,
                        "duration": resolved_duration,
                    }
                )

                # 2. Render Prompt using Jinja
                resolved_lighting = scene_lighting or defaults.cinematic_profile
                resolved_prompt = self.prompt_builder.build_prompt(
                    resolved_shot, defaults, resolved_lighting
                )
                resolved_negative_prompt = self.prompt_builder.build_negative_prompt(
                    resolved_shot, defaults
                )

                # 3. Resolve Reference Paths using AssetResolver
                resolved_references: list[str] = []
                for ref in shot.references:
                    # If reference matches a character or location, resolve to its master asset path
                    char_names = {c.name for c in episode.characters}
                    loc_names = {loc.name for loc in episode.locations}
                    if ref in char_names or ref in loc_names:
                        path = self.resolver.resolve_reference(ref)
                        resolved_references.append(str(path))
                    else:
                        resolved_references.append(ref)

                # 4. Resolve Output Filename/Path
                output_name = shot.output_filename or f"Shot{shot.shot_id.zfill(3)}.mp4"
                output_path = f"downloads/Episode{episode.episode_id.zfill(3)}/Scene{scene.scene_id.zfill(3)}/{output_name}"

                jobs.append(
                    {
                        "job_id": f"Scene{scene.scene_id}_Shot{shot.shot_id}",
                        "scene_id": scene.scene_id,
                        "shot_id": shot.shot_id,
                        "generation_type": shot.generation_type,
                        "prompt": resolved_prompt,
                        "negative_prompt": resolved_negative_prompt,
                        "references": resolved_references,
                        "duration": resolved_shot.duration,
                        "output_path": output_path,
                        "provider": resolved_shot.provider,
                    }
                )

        return {
            "episode_id": episode.episode_id,
            "title": episode.title,
            "jobs": jobs,
        }

    def generate_execution_graph(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Build dependency graph between compiled jobs."""
        nodes: list[str] = []
        edges: list[dict[str, str]] = []

        # Populate nodes
        for job in plan["jobs"]:
            nodes.append(job["job_id"])

        # Determine edges based on generation_type and references dependencies
        # Example: image-to-video jobs depend on the output of a preceding text-to-image job if references match
        for job in plan["jobs"]:
            job_id = job["job_id"]
            generation_type = job["generation_type"]

            if generation_type == "image_to_video":
                # Look for matching target jobs inside references
                for ref in job["references"]:
                    # e.g., if a reference is "Scene1_Shot1"
                    for other_job in plan["jobs"]:
                        other_id = other_job["job_id"]
                        if other_id in ref or other_job["output_path"] in ref:
                            edges.append({"from": other_id, "to": job_id})

        return {
            "nodes": nodes,
            "edges": edges,
        }
