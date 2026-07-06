#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import tempfile
from PIL import Image

# Import dependencies
try:
    from effects import generate_ken_burns, OPENCV_AVAILABLE
    from timeline import sync_timeline_and_mix_audio
    from subtitles import generate_srt
except ImportError:
    # Fallback paths
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from effects import generate_ken_burns, OPENCV_AVAILABLE
    from timeline import sync_timeline_and_mix_audio
    from subtitles import generate_srt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_DIR = os.path.join(BASE_DIR, "Metadata")
ASSETS_FILE = os.path.join(METADATA_DIR, "assets.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")

def load_assets_catalog():
    if not os.path.exists(ASSETS_FILE):
        return {}
    with open(ASSETS_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    return {item["id"]: item for item in catalog}

def composite_scene_image(bg_path, char_path, output_path):
    """Composite a transparent character image onto a background image."""
    try:
        bg = Image.open(bg_path).convert("RGBA")
        char = Image.open(char_path).convert("RGBA")
        
        # Resize character to fit background height gracefully (e.g. 90% of background height)
        target_h = int(bg.height * 0.9)
        aspect_ratio = char.width / char.height
        target_w = int(target_h * aspect_ratio)
        char_resized = char.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Position at the bottom center
        paste_x = (bg.width - char_resized.width) // 2
        paste_y = bg.height - char_resized.height
        
        # Composite
        bg.paste(char_resized, (paste_x, paste_y), char_resized)
        bg.convert("RGB").save(output_path, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"Error compositing {bg_path} and {char_path}: {e}")
        return False

def apply_post_processing(input_video, output_video, duration, overlay_effects=None):
    """
    Applies cinematic post-processing overlays (vignette, black bars, grain, grading).
    """
    if not overlay_effects:
        overlay_effects = []
        
    filters = []
    
    # 1. Vignette
    filters.append("vignette=angle=0.15")
        
    # 2. Cinematic Black Bars (Letterbox)
    filters.append("drawbox=y=0:h=80:color=black:t=fill")
    filters.append(f"drawbox=y=ih-80:h=80:color=black:t=fill")
    
    # 3. Film Grain
    if "grain" in overlay_effects or "dust" in overlay_effects:
        filters.append("noise=alls=12:allf=t+u")
        
    # 4. Color Grading (Warm/Cool)
    if "warm" in overlay_effects:
        filters.append("eq=saturation=1.15:contrast=1.05")
    else:
        filters.append("eq=saturation=1.05:contrast=1.02")
        
    filter_str = ", ".join(filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", filter_str,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_video
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_episode(episode_json_path, output_name="episode_render.mp4"):
    """
    Renders an entire episode based on the Episode JSON.
    Automatically syncs audio, generates subtitles, and merges them.
    """
    if not os.path.exists(episode_json_path):
        print(f"Error: Episode script not found at {episode_json_path}")
        return False
        
    temp_files = []
    
    temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_audio.close()
    temp_files.append(temp_audio.name)
    
    temp_srt = tempfile.NamedTemporaryFile(suffix=".srt", delete=False)
    temp_srt.close()
    temp_files.append(temp_srt.name)
    
    # Step 1: Sync timeline and build continuous audio track
    print("\n--- Stage 3: Audio Timeline Sync ---")
    if not sync_timeline_and_mix_audio(episode_json_path, temp_audio.name):
        print("Error: Audio synchronization failed.")
        return False
        
    # Reload episode data after duration updates
    with open(episode_json_path, "r", encoding="utf-8") as f:
        episode_data = json.load(f)
        
    # Step 2: Generate subtitles SRT (for export/raw distribution)
    print("--- Stage 3: Subtitle Generation ---")
    generate_srt(episode_data, temp_srt.name)
    
    # Step 3: Render visual scenes
    print("\n--- Stage 2: Visual Scene Composition & Ken Burns ---")
    catalog = load_assets_catalog()
    scenes = episode_data.get("scenes", [])
    scene_videos = []
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for idx, scene in enumerate(scenes, 1):
        duration = scene.get("duration", 8.0)
        visuals = scene.get("visuals", [])
        narration = scene.get("narration", "")
        
        bg_asset = None
        char_asset = None
        
        for vis_id in visuals:
            asset = catalog.get(vis_id)
            if asset:
                if asset["type"] == "background":
                    bg_asset = asset
                elif asset["type"] == "character":
                    char_asset = asset
                    
        resolved_img_path = None
        if bg_asset and char_asset:
            bg_full = os.path.join(BASE_DIR, bg_asset["file"])
            char_full = os.path.join(BASE_DIR, char_asset["file"])
            temp_composite = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_composite.close()
            temp_files.append(temp_composite.name)
            
            if composite_scene_image(bg_full, char_full, temp_composite.name):
                resolved_img_path = temp_composite.name
        elif bg_asset:
            resolved_img_path = os.path.join(BASE_DIR, bg_asset["file"])
        elif char_asset:
            resolved_img_path = os.path.join(BASE_DIR, char_asset["file"])
            
        if not resolved_img_path or not os.path.exists(resolved_img_path):
            fallback = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            fallback.close()
            temp_files.append(fallback.name)
            Image.new("RGB", (1920, 1080), (10, 10, 15)).save(fallback.name)
            resolved_img_path = fallback.name
            
        scene_temp_output = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        scene_temp_output.close()
        temp_files.append(scene_temp_output.name)
        
        motion = scene.get("effects", {}).get("motion", "random")
        
        # Pass narration text to draw subtitle directly on frames
        success = generate_ken_burns(
            image_path=resolved_img_path,
            output_path=scene_temp_output.name,
            duration=duration,
            motion_type=motion,
            subtitle_text=narration
        )
        
        if success:
            processed_temp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            processed_temp.close()
            temp_files.append(processed_temp.name)
            
            overlays = scene.get("effects", {}).get("overlays", [])
            apply_post_processing(scene_temp_output.name, processed_temp.name, duration, overlays)
            scene_videos.append(processed_temp.name)
        else:
            print(f"Failed to generate video for scene {idx}")
            
    if not scene_videos:
        print("Error: No scenes were successfully rendered.")
        return False
        
    # Step 4: Concatenate scene videos
    print("\n--- Concat Video Track ---")
    concat_list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for video_path in scene_videos:
            f.write(f"file '{video_path}'\n")
            
    final_raw_video = os.path.join(OUTPUT_DIR, "final_raw_video.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        final_raw_video
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Step 5: Merge Audio (Subtitles are already burned directly into frames)
    print("\n--- Final Composite: Adding Audio Track ---")
    final_output = os.path.join(OUTPUT_DIR, output_name)
    
    composite_cmd = [
        "ffmpeg", "-y",
        "-i", final_raw_video,
        "-i", temp_audio.name,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        final_output
    ]
    
    subprocess.run(composite_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Clean up temp files
    for temp in temp_files:
        try:
            os.remove(temp)
        except:
            pass
    try:
        os.remove(concat_list_path)
        os.remove(final_raw_video)
    except:
        pass
        
    if os.path.exists(final_output):
        print(f"\n✨ Rendering Complete! Final episode rendered to: {final_output}")
        # Copy SRT next to output
        external_srt = os.path.splitext(final_output)[0] + ".srt"
        try:
            with open(external_srt, "w", encoding="utf-8") as dest:
                with open(temp_srt.name, "r", encoding="utf-8") as src:
                    dest.write(src.read())
            print(f"SRT subtitle file saved next to video: {external_srt}")
        except:
            pass
        return final_output
    else:
        print("Error compiling final video output.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        render_episode(sys.argv[1])
    else:
        print("Usage: python3 renderer.py <episode_json_path>")
