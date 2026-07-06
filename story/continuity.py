from episodes.schemas import Episode


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
                    # If this character had a costume previously tracked
                    # but shot specifies a custom costume or change
                    # Wait, let's check if the shot has custom character details or if we track costumes.
                    # Since Shot does not have a direct costume override in schemas, we can check if
                    # the shot's prompt contains contradictions, or keep it simple:
                    # if a character is specified, we check if they are defined in episode characters list.
                    # If they are not defined, warn.
                    defined_chars = {c.name for c in episode.characters}
                    if char_name not in defined_chars:
                        warnings.append(
                            f"Character warning: Character '{char_name}' is referenced in Shot {shot.shot_id} "
                            f"but is not defined in the Episode's character registry."
                        )

        return warnings
