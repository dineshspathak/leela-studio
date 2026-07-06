# Rendering Profiles Configuration

Export Profiles allow users to target specific platforms without updating core rendering code. All configurations are stored as YAML files under `profiles/`.

## 📁 Standard Profiles

### 1. YouTube 1080p (`profiles/youtube.yaml`)
Targeting high-quality widescreen video:
```yaml
name: "youtube"
resolution: "1920x1080"
aspect_ratio: "16:9"
fps: 24
video_codec: "libx264"
audio_codec: "aac"
bitrate: "8M"
container: "mp4"
```

### 2. YouTube Shorts / Instagram Reels (`profiles/shorts.yaml`)
Targeting vertical format:
```yaml
name: "shorts"
resolution: "1080x1920"
aspect_ratio: "9:16"
fps: 30
video_codec: "libx264"
audio_codec: "aac"
bitrate: "6M"
container: "mp4"
```

### 3. Instagram Feed (`profiles/instagram.yaml`)
Square aspect ratio:
```yaml
name: "instagram"
resolution: "1080x1080"
aspect_ratio: "1:1"
fps: 30
video_codec: "libx264"
audio_codec: "aac"
bitrate: "4M"
container: "mp4"
```

### 4. Lossless Master (`profiles/master.yaml`)
Archive quality preservation:
```yaml
name: "master"
resolution: "3840x2160"
aspect_ratio: "16:9"
fps: 24
video_codec: "dnxhr"
audio_codec: "pcm_s16le"
bitrate: "lossless"
container: "mov"
```
