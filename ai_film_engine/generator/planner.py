from typing import Any

from pydantic import BaseModel


class QualityProfile(BaseModel):
    name: str
    resolution: str
    duration: float
    provider: str
    model: str
    budget: float


QUALITY_PROFILES = {
    "draft": QualityProfile(
        name="draft",
        resolution="854x480",
        duration=2.0,
        provider="pixverse",
        model="v1",
        budget=10,
    ),
    "standard": QualityProfile(
        name="standard",
        resolution="1280x720",
        duration=4.0,
        provider="pixverse",
        model="v2",
        budget=25,
    ),
    "cinematic": QualityProfile(
        name="cinematic",
        resolution="1920x1080",
        duration=6.0,
        provider="pixverse",
        model="v2",
        budget=50,
    ),
    "premium": QualityProfile(
        name="premium",
        resolution="3840x2160",
        duration=10.0,
        provider="google_veo",
        model="v1",
        budget=100,
    ),
}


class UniversalPlanner:
    def __init__(self, profile_name: str = "standard"):
        self.profile = QUALITY_PROFILES.get(
            profile_name.lower(), QUALITY_PROFILES["standard"]
        )

    def plan_generation(
        self,
        episode_data: dict[str, Any],
        resolved_matches: dict[str, Any],
        provider_health: dict[str, Any],
    ) -> dict[str, Any]:
        """Formulate execution plans, matching reused assets versus new generation jobs."""
        manifest = {
            "planned_jobs": [],
            "reused_assets": [],
            "new_assets": [],
            "provider_selection": {},
            "dependencies": {},
            "estimated_credits": 0.0,
            "estimated_duration": 0.0,
            "quality_profile": self.profile.name,
        }

        # Scan scenes and shots
        for scene in episode_data.get("scenes", []):
            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id")
                # Check if resolved/matched
                match = resolved_matches.get(shot_id)
                if match and match.matched:
                    manifest["reused_assets"].append(
                        {
                            "shot_id": shot_id,
                            "path": match.asset_path,
                            "confidence": match.confidence,
                            "match_level": match.match_level,
                        }
                    )
                else:
                    # Choose provider based on profile & health availability
                    chosen_prov = self.profile.provider
                    if provider_health.get(chosen_prov, {}).get("status") != "healthy":
                        # Fallback to pixverse
                        chosen_prov = "pixverse"

                    manifest["new_assets"].append(shot_id)
                    manifest["planned_jobs"].append(
                        {
                            "job_id": f"job_{shot_id}",
                            "shot_id": shot_id,
                            "provider": chosen_prov,
                            "model": self.profile.model,
                            "resolution": self.profile.resolution,
                            "duration": self.profile.duration,
                        }
                    )
                    manifest["provider_selection"][shot_id] = chosen_prov

                    # Estimate
                    manifest["estimated_credits"] += self.profile.budget
                    manifest["estimated_duration"] += self.profile.duration * 1.5

        return manifest
