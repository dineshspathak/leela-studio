from pathlib import Path
from typing import Any


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
