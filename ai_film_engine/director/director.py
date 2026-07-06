from typing import Any

from ai_film_engine.core.episodes.schemas import Episode
from ai_film_engine.director.cinematography import CinematographyEngine
from ai_film_engine.director.continuity import QualityChecker
from ai_film_engine.director.state import StateEngine
from ai_film_engine.director.storyboard import StoryboardBuilder


class DirectorEngine:
    def __init__(self, templates_dir: str = "prompt_templates"):
        self.cinematography = CinematographyEngine()
        self.state_engine = StateEngine()
        self.checker = QualityChecker()
        self.storyboard_builder = StoryboardBuilder()

    def process_episode(
        self,
        episode: Episode,
        budget_limit: int = 15,  # Default budget limit
    ) -> dict[str, Any]:
        """Convert Episode Story DSL into complete shot designs, optimizing under budget constraints."""
        shots: list[dict[str, Any]] = []

        # 1. Initialize character registry in State Engine
        for char in episode.characters:
            self.state_engine.register_character(char.name, char.costume)

        # 2. Design initial shots list
        for scene in episode.scenes:
            scene_loc = scene.location or "unspecified"
            scene_lighting = scene.lighting_default or "soft"

            for idx, shot in enumerate(scene.shots):
                job_id = f"Scene{scene.scene_id}_Shot{shot.shot_id}"

                # Deduce shot importance score
                if "divine" in shot.prompt.lower() or idx == 0:
                    importance = "HERO"
                elif len(shot.characters) > 0:
                    importance = "IMPORTANT"
                else:
                    importance = "BACKGROUND"

                # Recommending provider flow & credits
                provider_flow, credits = self._recommend_provider_flow(
                    importance, shot.generation_type
                )

                # Design shot cinematography
                design = self.cinematography.design_shot(
                    shot_prompt=shot.prompt,
                    importance=importance,
                    time_of_day=(
                        "night"
                        if "night" in scene_lighting.lower()
                        or "torch" in scene_lighting.lower()
                        else "day"
                    ),
                    environment=scene_loc,
                    is_action="run" in shot.prompt.lower()
                    or "storm" in shot.prompt.lower(),
                )

                shots.append(
                    {
                        "job_id": job_id,
                        "scene_id": scene.scene_id,
                        "shot_id": shot.shot_id,
                        "prompt": shot.prompt,
                        "importance": importance,
                        "provider_flow": provider_flow,
                        "credits": credits,
                        **design,
                    }
                )

        # 3. Dynamic Credit Optimizer Loop
        shots = self._optimize_credits(shots, budget_limit)

        # Run Quality Continuity Checks
        self.checker.verify_episode_continuity(shots)

        # Build Storyboard outputs
        self.storyboard_builder.build_storyboard_files(episode.title, shots)

        # Generate Notes
        self._generate_director_notes(episode.title, shots)
        self._generate_production_notes(episode.title, shots)

        return {
            "title": episode.title,
            "shots": shots,
        }

    def _recommend_provider_flow(
        self, importance: str, gen_type: str
    ) -> tuple[str, int]:
        """Provider decision logic: recommends cheapest flow maintaining visual standards."""
        if gen_type == "existing_asset":
            return "existing_asset (cheapest option, using archived cache)", 0

        if importance == "HERO":
            return (
                "PixVerse (highest resolution video generation for critical beats)",
                10,
            )
        elif importance == "IMPORTANT":
            return "image_animation (animate master character portrait)", 5
        else:
            return "text_to_image (static background asset generation)", 1

    def _optimize_credits(
        self, shots: list[dict[str, Any]], budget: int
    ) -> list[dict[str, Any]]:
        """Automatically merge/downgrade shots to fit budget limits."""
        total_credits = sum(s["credits"] for s in shots)
        if total_credits <= budget:
            return shots

        # Budget exceeded: Start Optimization Loop
        # Step 1: Downgrade BACKGROUND / IMPORTANT shots to static/existing assets
        for s in shots:
            if s["importance"] == "IMPORTANT":
                s["importance"] = "BACKGROUND"
                s["provider_flow"] = "text_to_image (static image fallback)"
                s["credits"] = 1
            total_credits = sum(s["credits"] for s in shots)
            if total_credits <= budget:
                break

        # Step 2: Merge consecutive identical background shots if budget still exceeded
        if total_credits > budget:
            merged_shots = []
            last_prompt = None
            for s in shots:
                if s["prompt"] == last_prompt and s["importance"] == "BACKGROUND":
                    # Skip duplicate shot to merge
                    continue
                merged_shots.append(s)
                last_prompt = s["prompt"]
            shots = merged_shots

        return shots

    def _generate_director_notes(self, title: str, shots: list[dict[str, Any]]):
        lines = [
            f"# Director Notes - {title}",
            "",
            "This file documents the cinematography and artistic rationale chosen for each scene.",
            "",
        ]
        for s in shots:
            lines.append(f"### Job: {s['job_id']}")
            lines.append(
                f"- **Camera/Lens Choices**: Selected {s['framing']} with {s['movement']} because of its {s['importance']} significance."
            )
            lines.append(
                f"- **Atmospheric Lighting**: Rationale for '{s['lighting']}' to reinforce scene environment and key emotions ({s['emotion']})."
            )
            lines.append(f"- **Provider Choice**: Recommending {s['provider_flow']}.")
            lines.append("")

        with open("director_notes.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _generate_production_notes(self, title: str, shots: list[dict[str, Any]]):
        total_credits = sum(s["credits"] for s in shots)
        new_assets = sum(
            1
            for s in shots
            if "PixVerse" in s["provider_flow"] or "image" in s["provider_flow"]
        )
        reused = sum(1 for s in shots if "existing" in s["provider_flow"])

        lines = [
            f"# Production Notes - {title}",
            "",
            "## Resource Summaries",
            f"- **Estimated PixVerse Credits Required**: {total_credits}",
            f"- **New Generations Needed**: {new_assets}",
            f"- **Existing Assets Reused**: {reused}",
            f"- **Estimated Pipeline Render Time**: {len(shots) * 15} seconds",
            "",
            "## Shot List Details",
        ]
        for s in shots:
            lines.append(
                f"- {s['job_id']}: {s['provider_flow']} (Credits: {s['credits']})"
            )

        with open("production_notes.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
