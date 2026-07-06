# Render Graph (RenderGraph.json)

The Render Graph isolates cinematic storytelling intent from the underlying FFmpeg commands, allowing the pipeline to remain clean, reproducible, and easy to extend.

## 🏗️ Structure

```json
{
  "inputs": [
    {
      "id": 0,
      "path": "downloads/Episode001/Scene001/Shot001.png"
    },
    {
      "id": 1,
      "path": "downloads/Episode001/Scene001/Shot002.mp4"
    }
  ],
  "filters": [
    {
      "expr": "[0:v][1:v]concat=n=2:v=1:a=0[outv]"
    }
  ],
  "outputs": [
    {
      "map": "outv",
      "codec": "libx264",
      "bitrate": "8M",
      "path": "Krishna Birth Story.mp4"
    }
  ]
}
```

---

## 🏃 Workflow
1. The Storyboard and Execution Plan compile clips into a scene graph.
2. The scene graph tracks construct input lists and apply effect plugins (e.g. Ken Burns, Vignettes) and transition handlers.
3. Compiles a flat JSON object `RenderGraph.json` mapping all paths and filters.
4. The command compiler parses the JSON into direct FFmpeg instructions, avoiding any hardcoded formatting loops.
