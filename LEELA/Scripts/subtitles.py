#!/usr/bin/env python3
import os
import sys
import json

def format_srt_time(seconds):
    """Convert float seconds to SRT time format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def generate_srt(episode_data, output_srt_path):
    """
    Generate an SRT file based on episode scenes and their durations.
    """
    scenes = episode_data.get("scenes", [])
    
    current_time = 0.0
    srt_lines = []
    
    for idx, scene in enumerate(scenes, 1):
        duration = scene.get("duration", 8.0)
        narration = scene.get("narration", "")
        
        if not narration.strip():
            current_time += duration
            continue
            
        start_time_str = format_srt_time(current_time)
        end_time_str = format_srt_time(current_time + duration)
        
        # Format SRT entry
        srt_lines.append(str(idx))
        srt_lines.append(f"{start_time_str} --> {end_time_str}")
        srt_lines.append(narration.strip())
        srt_lines.append("")  # Empty line separator
        
        current_time += duration
        
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
        
    print(f"Subtitles generated successfully at: {output_srt_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 2:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_srt(data, sys.argv[2])
    else:
        print("Usage: python3 subtitles.py <episode_json> <output_srt>")
