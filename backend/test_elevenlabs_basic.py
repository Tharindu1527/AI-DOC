#!/usr/bin/env python3
"""
Test ElevenLabs API with basic text-to-speech functionality
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs_basic():
    """Test ElevenLabs API with basic TTS"""
    print("🔍 Testing ElevenLabs API with basic TTS...")
    try:
        from elevenlabs import generate, set_api_key
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        
        set_api_key(api_key)
        
        # Try to generate audio without listing voices
        audio = generate(
            text="Hello, this is a test.",
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        print("✅ ElevenLabs Basic TTS: WORKING")
        print(f"Generated audio: {len(audio) if audio else 0} bytes")
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs Basic TTS: FAILED - {str(e)}")
        return False

if __name__ == "__main__":
    test_elevenlabs_basic()
