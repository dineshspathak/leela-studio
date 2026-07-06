import os
import re
import asyncio
import edge_tts

async def synthesize_chunk(text, voice, output_path):
    # Clean out explicit (pause) labels but keep standard punctuation
    cleaned_text = re.sub(r'\(pause\)', '...', text)
    cleaned_text = cleaned_text.strip()
    
    print(f"Synthesizing to {output_path}...")
    communicate = edge_tts.Communicate(cleaned_text, voice)
    await communicate.save(output_path)

def parse_voice_package(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Capture only the text block under Narration Text and stop before the next metadata bullet point (*   **)
    chunk_pattern = re.compile(r'### \*\*Chunk\s+(\d+)[^*]*\*\*.*?Narration(?:\s+Text)?\*\*:\s*\n(.*?)(?=\n\s*\*\s+\*\*|\n###|\Z)', re.DOTALL | re.IGNORECASE)
    matches = chunk_pattern.findall(content)
    chunks = []
    for match in matches:
        chunk_num = match[0]
        text = match[1].strip()
        chunks.append((chunk_num, text))
        
    return chunks

async def main():
    voice = "hi-IN-MadhurNeural"  # Canonical cinematic male voice
    
    # 1. Process V001
    v001_pkg = "/Users/dinesh/.gemini/antigravity-ide/brain/60d2a717-8ad4-4681-ae8d-5000a4775921/VOICE_PACKAGE_V001_v2.md"
    v001_chunks = parse_voice_package(v001_pkg)
    if v001_chunks:
        print(f"Found {len(v001_chunks)} chunks for V001.")
        os.makedirs("01_EPISODES/V001/Audio_Generated", exist_ok=True)
        for num, text in v001_chunks:
            out_file = f"01_EPISODES/V001/Audio_Generated/V001_Chunk_{num}.mp3"
            await synthesize_chunk(text, voice, out_file)
            
    # 2. Process V002
    v002_pkg = "/Users/Dinesh/Downloads/LEELA-STUDIOS/01_EPISODES/V002_PUTANA_VADH/VOICE_PACKAGE_V002_FINAL.md"
    v002_chunks = parse_voice_package(v002_pkg)
    if v002_chunks:
        print(f"Found {len(v002_chunks)} chunks for V002.")
        os.makedirs("01_EPISODES/V002_PUTANA_VADH/Audio_Generated", exist_ok=True)
        for num, text in v002_chunks:
            out_file = f"01_EPISODES/V002_PUTANA_VADH/Audio_Generated/V002_Chunk_{num}.mp3"
            await synthesize_chunk(text, voice, out_file)

if __name__ == "__main__":
    asyncio.run(main())
