import os
import subprocess

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def main():
    # Directories
    audio_dir = "01_EPISODES/V001/Audio_Generated"
    img_dir = "01_EPISODES/V001"
    output_dir = "01_EPISODES/V001/Video_Rendered"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Mapping chunks to images
    # 7 chunks total
    mappings = [
        ("V001_Chunk_1.mp3", "prison_cell_wide.png"),
        ("V001_Chunk_2.mp3", "wedding_scene.png"),
        ("V001_Chunk_3.mp3", "prison_cell_wide.png"),
        ("V001_Chunk_4.mp3", "vishnu_appears.png"),
        ("V001_Chunk_5.mp3", "vishnu_appears.png"),
        ("V001_Chunk_6.mp3", "yamuna_crossing.png"),
        ("V001_Chunk_7.mp3", "baby_krishna_yashoda.png"),
    ]
    
    segment_files = []
    
    for idx, (audio_file, img_file) in enumerate(mappings):
        audio_path = os.path.join(audio_dir, audio_file)
        img_path = os.path.join(img_dir, img_file)
        segment_path = os.path.join(output_dir, f"segment_{idx+1}.mp4")
        
        # Check if files exist (handle possible chunk filename naming variation)
        if not os.path.exists(audio_path):
            # Try V001_Chunk_01.mp3 format
            alt_audio_file = audio_file.replace("Chunk_", "Chunk_0")
            audio_path = os.path.join(audio_dir, alt_audio_file)
            
        if not os.path.exists(audio_path) or not os.path.exists(img_path):
            print(f"Skipping segment {idx+1} due to missing files: {audio_path} or {img_path}")
            continue
            
        print(f"Compiling segment {idx+1} ({audio_file} + {img_file})...")
        
        # ffmpeg command to create still video from image and audio
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            segment_path
        ]
        
        if run_command(cmd):
            segment_files.append(segment_path)
            
    if not segment_files:
        print("No segments were compiled successfully.")
        return
        
    # Concatenate all segments
    print("Concatenating segments...")
    concat_list_path = os.path.join(output_dir, "segments.txt")
    with open(concat_list_path, "w") as f:
        for file in segment_files:
            # write absolute or relative path
            f.write(f"file '{os.path.basename(file)}'\n")
            
    final_output = "01_EPISODES/V001/V001_FINAL_RENDER.mp4"
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        final_output
    ]
    
    if run_command(concat_cmd):
        print(f"\n🎉 Success! Final video rendered at: {final_output}")
    else:
        print("\n❌ Failed to concatenate segments.")

if __name__ == "__main__":
    main()
