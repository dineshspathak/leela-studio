import asyncio
import edge_tts

async def generate_samples():
    text = "एक जेल। बंद दरवाज़े। लोहे की ज़ंजीरें। आज रात... सातवीं नहीं — आठवीं संतान आने वाली है।"
    
    # Generate Swara (Female)
    print("Generating Swara (Female) voice sample...")
    await edge_tts.Communicate(text, "hi-IN-SwaraNeural").save("04_TOOLS/test_swara.mp3")
    
    # Generate Madhur (Male)
    print("Generating Madhur (Male) voice sample...")
    await edge_tts.Communicate(text, "hi-IN-MadhurNeural").save("04_TOOLS/test_madhur.mp3")
    
    print("Done! Check 04_TOOLS folder for test_swara.mp3 and test_madhur.mp3")

if __name__ == "__main__":
    asyncio.run(generate_samples())
