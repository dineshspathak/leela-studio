import os
import re
from google import genai
from google.genai import types

def parse_voice_package(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Capture only the text block under Narration Text and stop before the next metadata bullet point (*   **)
    chunk_pattern = re.compile(
        r'### \*\*Chunk\s+(\d+)[^*]*\*\*.*?Narration(?:\s+Text)?\*\*:\s*\n(.*?)(?=\n\s*\*\s+\*\*|\n###|\Z)', 
        re.DOTALL | re.IGNORECASE
    )
    matches = chunk_pattern.findall(content)
    
    chunks = []
    for match in matches:
        chunk_num = match[0]
        text = match[1].strip()
        chunks.append((chunk_num, text))
        
    return chunks

def generate_gemini_audio(text, api_key, output_path):
    client = genai.Client(api_key=api_key)
    
    prompt = (
        "Please read this narration text in Hindi with a natural Indian accent, "
        "warm storytelling, calm spiritual tone, and slow cinematic pacing. "
        "Do not add any introductory or concluding text, only read the text provided:\n\n"
        f"{text}"
    )
    
    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Charon"  # Charon is the deep, calm, confident male voice
                )
            )
        )
    )
    
    print(f"Requesting Gemini API for {output_path}...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt,
            config=config
        )
        
        audio_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                audio_bytes = part.inline_data.data
                break
                
        if audio_bytes:
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"✅ Success! Saved to {output_path}")
            return True
        else:
            print("❌ Error: No audio data found in the response parts.")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred calling Gemini: {str(e)}")
        return False

def main():
    api_key = "AIzaSyDuxBg70VCCIVrafDR4JKgJ21es96340IU"
    
    # 1. Process V001
    v001_pkg = "/Users/dinesh/.gemini/antigravity-ide/brain/60d2a717-8ad4-4681-ae8d-5000a4775921/VOICE_PACKAGE_V001_v2.md"
    v001_chunks = parse_voice_package(v001_pkg)
    if v001_chunks:
        print(f"Found {len(v001_chunks)} chunks for V001.")
        os.makedirs("01_EPISODES/V001/Audio_Generated", exist_ok=True)
        for num, text in v001_chunks:
            # Output format: V001_01.wav, V001_02.wav, etc.
            out_file = f"01_EPISODES/V001/Audio_Generated/V001_{num}.wav"
            generate_gemini_audio(text, api_key, out_file)
            
    # 2. Process V002
    v002_pkg = "/Users/Dinesh/Downloads/LEELA-STUDIOS/01_EPISODES/V002_PUTANA_VADH/VOICE_PACKAGE_V002_FINAL.md"
    v002_chunks = parse_voice_package(v002_pkg)
    if v002_chunks:
        print(f"Found {len(v002_chunks)} chunks for V002.")
        os.makedirs("01_EPISODES/V002_PUTANA_VADH/Audio_Generated", exist_ok=True)
        for num, text in v002_chunks:
            out_file = f"01_EPISODES/V002_PUTANA_VADH/Audio_Generated/V002_{num}.wav"
            generate_gemini_audio(text, api_key, out_file)

if __name__ == "__main__":
    main()
