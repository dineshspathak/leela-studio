import os
import re
import base64
import requests

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

def synthesize_sarvam_chunk(text, api_key, output_path):
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Clean out explicit (pause) labels
    cleaned_text = re.sub(r'\(pause\)', ' ', text)
    cleaned_text = cleaned_text.strip()
    
    payload = {
        "text": cleaned_text,
        "speaker": "priya",
        "model": "bulbul:v3",
        "target_language_code": "hi-IN",
        "properties": {
            "pace": 1.1,
            "output_audio_codec": "mp3"
        }
    }
    
    print(f"Requesting Sarvam AI API for {output_path}...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error generating voice: {response.text}")
        return False
        
    try:
        res_data = response.json()
        base64_audio = res_data.get("audio")
        if not base64_audio:
            print("❌ Error: No audio key found in response.")
            return False
            
        audio_binary = base64.b64decode(base64_audio)
        
        with open(output_path, "wb") as f:
            f.write(audio_binary)
        print(f"✅ Success! Saved to {output_path}")
        return True
    except Exception as e:
        print(f"❌ Exception occurred parsing response: {str(e)}")
        return False

def main():
    api_key = "sk_01w5kuv5_dO7LMx2qfEvEFMEt6YLOfMXe"
    
    # 1. Process V001
    v001_pkg = "/Users/dinesh/.gemini/antigravity-ide/brain/60d2a717-8ad4-4681-ae8d-5000a4775921/VOICE_PACKAGE_V001_v2.md"
    v001_chunks = parse_voice_package(v001_pkg)
    if v001_chunks:
        print(f"Found {len(v001_chunks)} chunks for V001.")
        os.makedirs("01_EPISODES/V001/Audio_Generated", exist_ok=True)
        for num, text in v001_chunks:
            out_file = f"01_EPISODES/V001/Audio_Generated/V001_Chunk_{num}.mp3"
            synthesize_sarvam_chunk(text, api_key, out_file)
            
    # 2. Process V002
    v002_pkg = "/Users/Dinesh/Downloads/LEELA-STUDIOS/01_EPISODES/V002_PUTANA_VADH/VOICE_PACKAGE_V002_FINAL.md"
    v002_chunks = parse_voice_package(v002_pkg)
    if v002_chunks:
        print(f"Found {len(v002_chunks)} chunks for V002.")
        os.makedirs("01_EPISODES/V002_PUTANA_VADH/Audio_Generated", exist_ok=True)
        for num, text in v002_chunks:
            out_file = f"01_EPISODES/V002_PUTANA_VADH/Audio_Generated/V002_Chunk_{num}.mp3"
            synthesize_sarvam_chunk(text, api_key, out_file)

if __name__ == "__main__":
    main()
