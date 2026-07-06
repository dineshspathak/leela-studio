from ai_film_engine.core.episodes.schemas import Episode


def validate_episode(episode: Episode) -> list[str]:
    """Validate Episode structural logic, finding duplicates, missing references, and constraints."""
    errors: list[str] = []
    seen_shots = set()

    # Pre-load character and location sets for fast membership checks
    defined_characters = {c.name for c in episode.characters}
    defined_locations = {loc.name for loc in episode.locations}

    # Pre-load all job IDs
    defined_jobs = {
        f"Scene{s.scene_id}_Shot{sh.shot_id}" for s in episode.scenes for sh in s.shots
    }

    for scene in episode.scenes:
        if not scene.scene_id:
            errors.append(
                f"Scene error: Scene is missing scene_id (Title: {scene.title})"
            )

        for shot in scene.shots:
            # Check for duplicate shot IDs
            full_shot_id = f"{scene.scene_id}_{shot.shot_id}"
            if full_shot_id in seen_shots:
                errors.append(f"Duplicate Shot ID found: '{full_shot_id}'")
            seen_shots.add(full_shot_id)

            # Check prompt
            if not shot.prompt:
                errors.append(f"Shot '{full_shot_id}' is missing a prompt.")

            # Check duration
            duration = shot.duration or scene.duration_default or 5
            if duration <= 0:
                errors.append(
                    f"Shot '{full_shot_id}' has invalid duration: {duration}s"
                )
            elif duration > 30:
                errors.append(
                    f"Shot '{full_shot_id}' duration is too long: {duration}s (Max recommended 30s)"
                )

            # Check provider validation
            provider = (
                shot.provider
                or scene.provider_default
                or episode.global_defaults.provider
            )
            if provider.lower() not in ("pixverse", "mock", "dummy"):
                errors.append(
                    f"Shot '{full_shot_id}' uses unsupported provider: '{provider}'"
                )

            # Check characters exist in registry
            for char in shot.characters:
                if char not in defined_characters:
                    errors.append(
                        f"Shot '{full_shot_id}' references undefined character: '{char}'"
                    )

            # Check location exists in registry
            shot_loc = shot.location or scene.location
            if shot_loc and shot_loc not in defined_locations:
                errors.append(
                    f"Shot '{full_shot_id}' references undefined location: '{shot_loc}'"
                )

            # Check references exist
            for ref in shot.references:
                # Reference should either be another shot's output filename, or a master asset name, or a character name
                if (
                    ref not in defined_characters
                    and ref not in defined_locations
                    and ref not in defined_jobs
                    and not ref.endswith(".png")
                    and not ref.endswith(".mp4")
                ):
                    errors.append(
                        f"Shot '{full_shot_id}' references unresolved asset or shot: '{ref}'"
                    )

    return errors
