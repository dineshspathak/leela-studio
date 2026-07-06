from typing import Any


class AudioEngine:
    def mix_tracks(
        self,
        narration_path: str,
        bg_music_path: str,
        ambient_path: str | None = None,
        sfx_clips: list[dict[str, Any]] | None = None,
    ) -> str:
        """Construct FFmpeg audio filtergraph snippet to mix narration, music, ambient and SFX."""
        # Standard sidechain compression ducks music (input 1) under narration (input 0)
        # We model this using standard amix and sidechaincompress filters
        duck_filter = (
            "[0:a][1:a]sidechaincompress=threshold=0.15:ratio=4:release=500[ducked];"
            "[ducked]volume=0.4[ducked_vol]"
        )

        mix_inputs = "[0:a][ducked_vol]"
        if ambient_path:
            mix_inputs += "[2:a]"

        mix_filter = f"{mix_inputs}amix=inputs={mix_inputs.count('[')}:duration=first:dropout_transition=2"
        return f"{duck_filter};{mix_filter}"
