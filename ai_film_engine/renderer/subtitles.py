from pathlib import Path
from typing import Any


class SubtitleEngine:
    def build_subtitle_files(
        self, subtitle_clips: list[dict[str, Any]], base_name: str
    ) -> dict[str, Path]:
        """Convert subtitles dictionary items to SRT and ASS file formats."""
        srt_path = Path(f"{base_name}.srt")
        ass_path = Path(f"{base_name}.ass")

        # 1. Write SRT
        self._write_srt(subtitle_clips, srt_path)

        # 2. Write ASS
        self._write_ass(subtitle_clips, ass_path)

        return {"srt": srt_path, "ass": ass_path}

    def _write_srt(self, clips: list[dict[str, Any]], path: Path):
        lines = []
        for idx, clip in enumerate(clips, 1):
            start = self._format_timestamp(clip["start_time"])
            end = self._format_timestamp(clip["end_time"])
            text = clip["text"]
            lines.extend([str(idx), f"{start} --> {end}", text, ""])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_ass(self, clips: list[dict[str, Any]], path: Path):
        # Write basic ASS header with styles for cinematic look
        header = """[Script Info]
Title: LEELA Movie Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = [header]
        for clip in clips:
            start = self._format_timestamp_ass(clip["start_time"])
            end = self._format_timestamp_ass(clip["end_time"])
            text = clip["text"]
            lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _format_timestamp(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def _format_timestamp_ass(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)  # Centiseconds for ASS
        return f"{h:01}:{m:02}:{s:02}.{cs:02}"

    def get_burn_filter(self, srt_path: Path) -> str:
        """Return FFmpeg video filter to burn subtitles onto video."""
        # Convert path backslashes for Windows if needed
        safe_path = str(srt_path).replace("\\", "/")
        return f"subtitles='{safe_path}'"
