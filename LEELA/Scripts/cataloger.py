#!/usr/bin/env python3
import os
import json
import re

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
METADATA_DIR = os.path.join(BASE_DIR, "Metadata")
OUTPUT_FILE = os.path.join(METADATA_DIR, "assets.json")

# Allowed extensions
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg"}

# Keywords to detect
EMOTIONS = ["crying", "smiling", "sad", "happy", "angry", "resolute", "peaceful", "neutral", "sorrowful", "menacing", "warm"]
CAMERA_ANGLES = ["closeup", "wide", "mid", "ots", "establishing", "extreme_closeup"]

def parse_filename_meta(filename):
    """Extract emotion and camera angle from filename string."""
    name_clean = os.path.splitext(filename)[0].lower()
    
    detected_emotion = "neutral"
    for emotion in EMOTIONS:
        if emotion in name_clean:
            detected_emotion = emotion
            break
            
    detected_camera = "standard"
    for angle in CAMERA_ANGLES:
        if angle in name_clean:
            detected_camera = angle
            break
            
    return detected_emotion, detected_camera

def scan_assets():
    if not os.path.exists(ASSETS_DIR):
        print(f"Error: Assets directory does not exist at {ASSETS_DIR}")
        return
        
    catalog = []
    
    # 1. Scan Characters
    char_dir = os.path.join(ASSETS_DIR, "Characters")
    if os.path.exists(char_dir):
        for char_name in sorted(os.listdir(char_dir)):
            char_path = os.path.join(char_dir, char_name)
            if os.path.isdir(char_path):
                # Scan character files
                files = sorted([f for f in os.listdir(char_path) if os.path.splitext(f)[1].lower() in IMAGE_EXTS])
                for idx, file in enumerate(files, 1):
                    file_rel = os.path.relpath(os.path.join(char_path, file), BASE_DIR)
                    emotion, camera = parse_filename_meta(file)
                    
                    prefix = char_name.upper()
                    # Example ID: DEVAKI_001
                    asset_id = f"{prefix}_{idx:03d}"
                    
                    catalog.append({
                        "id": asset_id,
                        "type": "character",
                        "name": char_name,
                        "emotion": emotion,
                        "camera": camera,
                        "file": file_rel
                    })

    # 2. Scan Backgrounds
    bg_dir = os.path.join(ASSETS_DIR, "Backgrounds")
    if os.path.exists(bg_dir):
        for bg_name in sorted(os.listdir(bg_dir)):
            bg_path = os.path.join(bg_dir, bg_name)
            if os.path.isdir(bg_path):
                files = sorted([f for f in os.listdir(bg_path) if os.path.splitext(f)[1].lower() in IMAGE_EXTS])
                for idx, file in enumerate(files, 1):
                    file_rel = os.path.relpath(os.path.join(bg_path, file), BASE_DIR)
                    emotion, camera = parse_filename_meta(file)
                    
                    prefix = bg_name.upper()
                    asset_id = f"{prefix}_{idx:03d}"
                    
                    catalog.append({
                        "id": asset_id,
                        "type": "background",
                        "name": bg_name,
                        "camera": camera,
                        "file": file_rel
                    })

    # 3. Scan Videos
    video_dir = os.path.join(ASSETS_DIR, "Videos")
    if os.path.exists(video_dir):
        files = sorted([f for f in os.listdir(video_dir) if os.path.splitext(f)[1].lower() in VIDEO_EXTS])
        for idx, file in enumerate(files, 1):
            file_rel = os.path.relpath(os.path.join(video_dir, file), BASE_DIR)
            asset_id = f"VIDEO_{idx:03d}"
            
            catalog.append({
                "id": asset_id,
                "type": "video",
                "name": os.path.splitext(file)[0],
                "file": file_rel
            })

    # 4. Scan Audio
    audio_dir = os.path.join(ASSETS_DIR, "Audio")
    if os.path.exists(audio_dir):
        for category in ["Narration", "Music", "SFX"]:
            cat_path = os.path.join(audio_dir, category)
            if os.path.exists(cat_path):
                files = sorted([f for f in os.listdir(cat_path) if os.path.splitext(f)[1].lower() in AUDIO_EXTS])
                for idx, file in enumerate(files, 1):
                    file_rel = os.path.relpath(os.path.join(cat_path, file), BASE_DIR)
                    prefix = category.upper()
                    asset_id = f"{prefix}_{idx:03d}"
                    
                    catalog.append({
                        "id": asset_id,
                        "type": "audio",
                        "category": category.lower(),
                        "name": os.path.splitext(file)[0],
                        "file": file_rel
                    })

    # Save Catalog
    os.makedirs(METADATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    print(f"Catalog successfully generated with {len(catalog)} assets in {OUTPUT_FILE}")
    return catalog

if __name__ == "__main__":
    scan_assets()
