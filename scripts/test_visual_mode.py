import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.config import Config
from haitham_voice_agent.tts import get_tts

async def test_visual_mode():
    print("="*50)
    print("🧪 Testing Visual Mode (Silent TTS)")
    print("="*50)
    
    # 1. Verify Config
    print(f"\n📋 Configuration Check:")
    print(f"TTS_ENABLED: {Config.TTS_ENABLED} (Expected: False)")
    print(f"SOUND_EFFECTS_ENABLED: {Config.SOUND_EFFECTS_ENABLED} (Expected: True)")
    
    if Config.TTS_ENABLED:
        print("❌ Error: TTS should be disabled!")
        return
        
    # 2. Verify Sounds Exist
    print(f"\n🔊 Sound Files Check:")
    for name, path in Config.SOUNDS.items():
        exists = os.path.exists(path)
        status = "✅ Found" if exists else "❌ Missing"
        print(f"  - {name}: {status} ({path})")
        
    # 3. Test Speak (Should be silent + log)
    print(f"\n🔇 Testing Speak (Should be silent):")
    tts = get_tts()
    await tts.speak("This is a test message. You should NOT hear this voice, but you might hear a ping.")
    print("✅ Speak called (check logs for 'TTS Disabled')")
    
    # 4. Test Play Sound
    print(f"\n🔔 Testing System Sound (Ping):")
    await tts.play_sound("notification", wait=True)
    print("✅ Sound played")

if __name__ == "__main__":
    asyncio.run(test_visual_mode())
