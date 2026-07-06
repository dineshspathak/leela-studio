# Movie Rendering Engine Architecture

The Movie Rendering Engine compiles scene graph multi-tracks, transitions, effects, and subtitles into finished MP4 movies.

## 🏗️ Architecture

```mermaid
graph TD
    Graph["RenderGraph.json"]
    Renderer["MovieRendererEngine (engine.py)"]
    Timeline["SceneGraph (scene_graph.py)"]
    Audio["Audio Engine (audio.py)"]
    Subtitles["Subtitle Engine (subtitles.py)"]
    FFmpeg["FFmpeg Command Compiler (ffmpeg.py)"]
    
    subgraph Plugins
        Effects["Effect Plugins (plugins/*)"]
        Transitions["Transition Plugins (transitions/*)"]
    end

    Timeline --> Renderer
    Renderer --> Audio
    Renderer --> Subtitles
    Renderer --> Effects
    Renderer --> Transitions
    Renderer --> Graph
    Graph --> FFmpeg
    FFmpeg --> MP4["Episode001.mp4"]
```

---

## 💾 Render Cache
To speed up iterations:
1. Generates SHA256 signatures of plan contents.
2. If signature exists under `cache/renderer/`, copies cached MP4 instantly, skipping rendering.

---

## 🏃 Commands
- **Render full episode**:
  `python main.py render Episode001.json --profile youtube`
- **Render preview**:
  `python main.py preview Episode001.json`
- **One command production**:
  `python main.py make Episode001.json`
