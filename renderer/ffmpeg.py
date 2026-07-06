import json
from pathlib import Path
from typing import Any


class FFmpegCommandCompiler:
    def __init__(self, render_graph_path: str = "output/RenderGraph.json"):
        self.render_graph_path = Path(render_graph_path)

    def compile_graph_to_command(self, graph: dict[str, Any]) -> str:
        """Translate RenderGraph.json structural fields into an executable FFmpeg shell command."""
        inputs = graph.get("inputs", [])
        filters = graph.get("filters", [])
        outputs = graph.get("outputs", [])

        # 1. Parse inputs
        input_args = []
        for inp in inputs:
            input_args.append(f"-i {inp['path']}")

        # 2. Parse filtergraphs
        filter_complex = []
        for filt in filters:
            filter_complex.append(filt["expr"])

        filter_complex_arg = ""
        if filter_complex:
            joined = ";".join(filter_complex)
            filter_complex_arg = f'-filter_complex "{joined}"'

        # 3. Parse outputs
        output_args = []
        for out in outputs:
            mapping = f"-map {out['map']}" if "map" in out else ""
            codec = f"-c:v {out['codec']}" if "codec" in out else ""
            bitrate = f"-b:v {out['bitrate']}" if "bitrate" in out else ""
            output_args.append(f"{mapping} {codec} {bitrate} {out['path']}")

        # Compile final command line
        cmd = f"ffmpeg -y {' '.join(input_args)} {filter_complex_arg} {' '.join(output_args)}"
        return cmd

    def save_render_graph(self, graph: dict[str, Any]):
        """Persist structured RenderGraph.json for reproducible runs."""
        self.render_graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.render_graph_path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)
