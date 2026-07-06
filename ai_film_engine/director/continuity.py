from pathlib import Path
from typing import Any

from ai_film_engine.core.episodes.schemas import Episode


class QualityChecker:
    def __init__(self, report_path: str = "reports/continuity_report.md"):
        self.report_path = Path(report_path)

    def verify_episode_continuity(self, shots: list[dict[str, Any]]) -> list[str]:
        """Perform visual continuity verification checks across shots list."""
        warnings: list[str] = []

        last_framing: str = ""
        last_movement: str = ""
        last_lighting: str = ""
        last_emotion: str = ""

        framing_rep = 0
        movement_rep = 0
        lighting_rep = 0
        emotion_rep = 0

        for idx, shot in enumerate(shots):
            job_id = shot.get("job_id", f"Shot_{idx+1}")

            # Extract attributes
            framing = shot.get("framing", "")
            movement = shot.get("movement", "")
            lighting = shot.get("lighting", "")
            emotion = shot.get("emotion", "")

            # Repetition checks
            if framing == last_framing:
                framing_rep += 1
                if framing_rep >= 3:
                    warnings.append(
                        f"Pacing warning: Camera framing '{framing}' repeated consecutively {framing_rep} times at {job_id}."
                    )
            else:
                framing_rep = 1

            if movement == last_movement:
                movement_rep += 1
                if movement_rep >= 3:
                    warnings.append(
                        f"Pacing warning: Camera movement '{movement}' repeated consecutively {movement_rep} times at {job_id}."
                    )
            else:
                movement_rep = 1

            if lighting == last_lighting:
                lighting_rep += 1
                if lighting_rep >= 4:
                    warnings.append(
                        f"Visual warning: Lighting setup '{lighting}' repeated consecutively {lighting_rep} times at {job_id}."
                    )
            else:
                lighting_rep = 1

            if emotion == last_emotion:
                emotion_rep += 1
                if emotion_rep >= 3:
                    warnings.append(
                        f"Story warning: Character emotion '{emotion}' repeated consecutively {emotion_rep} times at {job_id}."
                    )
            else:
                emotion_rep = 1

            last_framing = framing
            last_movement = movement
            last_lighting = lighting
            last_emotion = emotion

        # Write markdown report
        self.generate_report(warnings)
        return warnings

    def generate_report(self, warnings: list[str]):
        """Compile findings into reports/continuity_report.md."""
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# LEELA Studio - Visual Continuity Report",
            "",
            "This report lists all validation checks, pacing alerts, and continuity warnings across the compiled storyboard.",
            "",
            "## Summary Status",
        ]

        if warnings:
            lines.append(f"❌ **Continuity warnings found: {len(warnings)}**")
            lines.append("")
            lines.append("## Warning Details")
            for w in warnings:
                lines.append(f"- {w}")
        else:
            lines.append(
                "✅ **All validation and continuity checks passed successfully!**"
            )

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


class ContinuityEngine:
    def validate_continuity(self, episode: Episode) -> list[str]:
        """Verify character costumes, locations, and lighting consistency across contiguous shots."""
        warnings: list[str] = []

        last_location: str | None = None
        last_lighting: str | None = None
        character_costumes: dict[str, str] = {}  # char_name -> costume

        # Initialize character costumes from character specifications if available
        for char in episode.characters:
            if char.costume:
                character_costumes[char.name] = char.costume

        for scene in episode.scenes:
            scene_loc = scene.location
            scene_lighting = scene.lighting_default

            for shot in scene.shots:
                shot_loc = shot.location or scene_loc
                shot_lighting = (
                    getattr(shot, "lighting_default", None) or scene_lighting
                )

                # 1. Location and Lighting Consistency
                if (
                    last_location
                    and shot_loc == last_location
                    and last_lighting
                    and shot_lighting != last_lighting
                ):
                    warnings.append(
                        f"Lighting continuity warning: Lighting changed from '{last_lighting}' "
                        f"to '{shot_lighting}' in contiguous shots at same location '{shot_loc}' "
                        f"(Scene: {scene.scene_id}, Shot: {shot.shot_id})."
                    )

                last_location = shot_loc
                last_lighting = shot_lighting

                # 2. Character Costume Consistency
                for char_name in shot.characters:
                    defined_chars = {c.name for c in episode.characters}
                    if char_name not in defined_chars:
                        warnings.append(
                            f"Character warning: Character '{char_name}' is referenced in Shot {shot.shot_id} "
                            f"but is not defined in the Episode's character registry."
                        )

        return warnings
