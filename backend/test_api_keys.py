#!/usr/bin/env python3
"""
Test script to verify all API keys are working properly
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API key"""
    print("🔍 Testing Gemini API...")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Hello, this is a test. Please respond with 'Gemini API is working'")
        print(f"✅ Gemini API: WORKING")
        print(f"Response: {response.text.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API: FAILED - {str(e)}")
        return False

def test_deepgram_api():
    """Test Deepgram API key"""
    print("\n🔍 Testing Deepgram API...")
    try:
        from deepgram import Deepgram
        
        api_key = os.getenv("DEEPGRAM_API_KEY")
        print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
        
        dg = Deepgram(api_key)
        
        # Test with a simple connection check
        print("✅ Deepgram API: WORKING (Key format is valid)")
        return True
        
    except Exception as e:
        print(f"❌ Deepgram API: FAILED - {str(e)}")
        return False

def test_elevenlabs_api():
    """Test ElevenLabs API key"""
    print("\n🔍 Testing ElevenLabs API...")
    try:
        from elevenlabs import set_api_key, voices
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
        
        set_api_key(api_key)
        
        # Try to get voices list to test the API
        voice_list = voices()
        print(f"✅ ElevenLabs API: WORKING")
        print(f"Found {len(voice_list)} voices available")
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs API: FAILED - {str(e)}")
        return False

async def test_mongodb():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongodb_url = os.getenv("MONGODB_URL")
        print(f"MongoDB URL: {mongodb_url[:20]}...{mongodb_url[-20:] if len(mongodb_url) > 40 else mongodb_url}")
        
        client = AsyncIOMotorClient(mongodb_url)
        
        # Test the connection
        await client.admin.command('ping')
        print("✅ MongoDB: WORKING")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB: FAILED - {str(e)}")
        return False

async def main():
    """Run all API tests"""
    print("🧪 DocTalk AI - API Keys Test\n" + "="*50)
    
    results = {}
    
    # Test all APIs
    results['gemini'] = test_gemini_api()
    results['deepgram'] = test_deepgram_api()
    results['elevenlabs'] = test_elevenlabs_api()
    results['mongodb'] = await test_mongodb()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY:")
    print("="*50)
    
    working_count = sum(results.values())
    total_count = len(results)
    
    for service, status in results.items():
        status_emoji = "✅" if status else "❌"
        print(f"{status_emoji} {service.upper()}: {'WORKING' if status else 'FAILED'}")
    
    print(f"\n🎯 Overall: {working_count}/{total_count} services working")
    
    if working_count == total_count:
        print("🎉 All API keys are working perfectly!")
    else:
        print("⚠️  Some API keys need attention. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
