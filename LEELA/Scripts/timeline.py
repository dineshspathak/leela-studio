#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_DIR = os.path.join(BASE_DIR, "Metadata")
ASSETS_FILE = os.path.join(METADATA_DIR, "assets.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")

def get_audio_duration(audio_path):
    """Retrieve duration of an audio file in seconds using ffprobe."""
    if not os.path.exists(audio_path):
        return 0.0
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Warning: Failed to probe duration of {audio_path}: {e}")
        return 0.0

def load_assets_catalog():
    if not os.path.exists(ASSETS_FILE):
        return {}
    with open(ASSETS_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    return {item["id"]: item for item in catalog}

def sync_timeline_and_mix_audio(episode_json_path, output_audio_path):
    """
    1. Reads narration audio files for each scene.
    2. Adjusts scene durations to match narration lengths.
    3. Builds a timeline of narration, music, and SFX.
    4. Generates an FFmpeg complex filtergraph to compile and mix all audio.
    """
    with open(episode_json_path, "r", encoding="utf-8") as f:
        episode_data = json.load(f)
        
    catalog = load_assets_catalog()
    scenes = episode_data.get("scenes", [])
    
    current_time = 0.0
    narration_segments = []
    sfx_segments = []
    
    # Check background music
    bg_music_asset = None
    music_id = episode_data.get("music")
    if music_id:
        bg_music_asset = catalog.get(music_id)
        
    modified_scenes = []
    
    for idx, scene in enumerate(scenes, 1):
        # Resolve narration audio
        narr_id = scene.get("audio", {}).get("narration")
        narr_asset = catalog.get(narr_id) if narr_id else None
        
        scene_duration = scene.get("duration", 8.0)
        
        if narr_asset:
            narr_path = os.path.join(BASE_DIR, narr_asset["file"])
            if os.path.exists(narr_path):
                narr_dur = get_audio_duration(narr_path)
                if narr_dur > 0:
                    scene_duration = narr_dur
                    narration_segments.append({
                        "file": narr_path,
                        "start": current_time,
                        "duration": narr_dur
                    })
        else:
            print(f"No narration asset found for scene {idx}, keeping duration {scene_duration}s")
            
        # Resolve SFX
        sfx_id = scene.get("audio", {}).get("sfx")
        sfx_asset = catalog.get(sfx_id) if sfx_id else None
        if sfx_asset:
            sfx_path = os.path.join(BASE_DIR, sfx_asset["file"])
            if os.path.exists(sfx_path):
                sfx_segments.append({
                    "file": sfx_path,
                    "start": current_time,
                    "duration": get_audio_duration(sfx_path)
                })
                
        # Update scene duration in modified structure
        scene["duration"] = scene_duration
        modified_scenes.append(scene)
        
        current_time += scene_duration
        
    total_duration = current_time
    print(f"Sync complete. Total adjusted episode duration: {total_duration:.2f} seconds.")
    
    # Save back updated durations to episode json
    episode_data["scenes"] = modified_scenes
    with open(episode_json_path, "w", encoding="utf-8") as f:
        json.dump(episode_data, f, indent=2, ensure_ascii=False)
        
    # Generate FFmpeg complex audio mixing script
    # Inputs:
    # 0, 1, 2... inputs are segment audios
    # We will construct a filtergraph that delays each segment and mixes them.
    inputs = []
    filter_elements = []
    
    # 1. Narration inputs
    for idx, seg in enumerate(narration_segments):
        inputs.extend(["-i", seg["file"]])
        # Delay filter: adelay=delay_ms|delay_ms
        delay_ms = int(seg["start"] * 1000)
        # Note: input index is idx
        filter_elements.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[narr_{idx}]")
        
    narr_count = len(narration_segments)
    
    # 2. SFX inputs
    for sfx_idx, seg in enumerate(sfx_segments):
        inputs.extend(["-i", seg["file"]])
        delay_ms = int(seg["start"] * 1000)
        inp_idx = narr_count + sfx_idx
        filter_elements.append(f"[{inp_idx}:a]adelay={delay_ms}|{delay_ms}[sfx_{sfx_idx}]")
        
    sfx_count = len(sfx_segments)
    
    # 3. BG Music input
    music_input_idx = narr_count + sfx_count
    music_present = False
    if bg_music_asset:
        music_path = os.path.join(BASE_DIR, bg_music_asset["file"])
        if os.path.exists(music_path):
            # Loop music to fit total duration
            inputs.extend(["-stream_loop", "-1", "-i", music_path])
            music_present = True
            
            # Ducking filter logic:
            # We construct a volume timeline filter.
            # Volume is 0.15 (-16dB) during narration segments, 0.40 otherwise
            vol_expr = "0.40"
            for seg in narration_segments:
                s = seg["start"]
                e = seg["start"] + seg["duration"]
                vol_expr = f"if(between(t,{s:.3f},{e:.3f}),0.10,{vol_expr})"
                
            # Apply volume timeline and trim music to total duration
            filter_elements.append(f"[{music_input_idx}:a]volume=eval=frame:volume='{vol_expr}',atrim=0:{total_duration:.3f}[bg_music]")
            
    # Mix everything
    # We mix all delayed narration elements and sfx elements and background music
    narr_outputs = [f"[narr_{i}]" for i in range(narr_count)]
    sfx_outputs = [f"[sfx_{i}]" for i in range(sfx_count)]
    
    mix_sources = narr_outputs + sfx_outputs
    if music_present:
        mix_sources.append("[bg_music]")
        
    if mix_sources:
        mix_str = "".join(mix_sources)
        filter_elements.append(f"{mix_str}amix=inputs={len(mix_sources)}:duration=first:dropout_transition=0[out_audio]")
        filter_str = "; ".join(filter_elements)
        
        cmd = [
            "ffmpeg", "-y"
        ] + inputs + [
            "-filter_complex", filter_str,
            "-map", "[out_audio]",
            "-t", f"{total_duration:.3f}",
            output_audio_path
        ]
        
        print("\nMixing audio layers with FFmpeg...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    else:
        # Create silent audio fallback
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", f"{total_duration:.3f}",
            output_audio_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True

if __name__ == "__main__":
    if len(sys.argv) > 2:
        sync_timeline_and_mix_audio(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python3 timeline.py <episode_json_path> <output_audio_path>")
