import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any, Optional
import google.generativeai as genai
from deepgram import Deepgram

# Enhanced ElevenLabs import handling with multiple fallbacks
ELEVENLABS_AVAILABLE = False
generate = None
set_api_key = None
ElevenLabs = None

try:
    from elevenlabs import generate, set_api_key
    ELEVENLABS_AVAILABLE = True
    print("✓ ElevenLabs classic API loaded")
except ImportError:
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import play, stream, save
        ELEVENLABS_AVAILABLE = True
        generate = None
        set_api_key = None
        print("✓ ElevenLabs new API loaded")
    except ImportError:
        print("⚠️  ElevenLabs not available. Text-to-speech will be disabled.")
        ELEVENLABS_AVAILABLE = False

from config import settings
import logging
import re

logger = logging.getLogger(__name__)

# Configure APIs
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
else:
    logger.warning("Gemini API key not provided")

if ELEVENLABS_AVAILABLE and set_api_key and settings.elevenlabs_api_key:
    set_api_key(settings.elevenlabs_api_key)

class VoiceService:
    def __init__(self):
        # Initialize Deepgram
        if settings.deepgram_api_key:
            self.deepgram = Deepgram(settings.deepgram_api_key)
        else:
            logger.warning("Deepgram API key not provided")
            self.deepgram = None
        
        # Initialize Gemini
        if settings.gemini_api_key:
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("Gemini API key not provided")
            self.gemini_model = None
        
        # Initialize ElevenLabs client for new API
        self.elevenlabs_client = None
        if ELEVENLABS_AVAILABLE and not generate and settings.elevenlabs_api_key:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=settings.elevenlabs_api_key)
                print("✓ ElevenLabs client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize ElevenLabs client: {e}")
        
        self.conversation_context = []
        self.available_doctors = [
            "Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", 
            "Dr. Davis", "Dr. Miller", "Dr. Wilson", "Dr. Moore"
        ]
        self.business_hours = {
            "start": 9,  # 9 AM
            "end": 17,   # 5 PM
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }

    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio using Deepgram with enhanced error handling"""
        if not self.deepgram:
            raise Exception("Deepgram not initialized - check API key")
        
        try:
            response = await self.deepgram.transcription.prerecorded(
                {'buffer': audio_data, 'mimetype': 'audio/wav'},
                {
                    'punctuate': True, 
                    'language': 'en',
                    'model': settings.deepgram_model,
                    'smart_format': True,
                    'diarize': False
                }
            )
            
            if response['results']['channels'][0]['alternatives']:
                transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
                confidence = response['results']['channels'][0]['alternatives'][0]['confidence']
                logger.info(f"Transcription confidence: {confidence}")
                return transcript
            return ""
            
        except Exception as e:
            logger.error(f"Deepgram transcription error: {str(e)}")
            raise Exception(f"Speech recognition failed: {str(e)}")

    async def generate_response(self, transcript: str) -> Dict[str, Any]:
        """Generate AI response using Gemini with enhanced medical context"""
        if not self.gemini_model:
            raise Exception("Gemini not initialized - check API key")
        
        try:
            # Add conversation context
            context = "\n".join([f"User: {item['user']}\nAI: {item['ai']}" for item in self.conversation_context[-3:]])
            
            current_time = datetime.now()
            available_times = self._get_available_time_slots()
            
            prompt = f"""You are DocTalk AI, a professional medical appointment assistant for a healthcare clinic.

Current time: {current_time.strftime('%Y-%m-%d %H:%M')}
Available doctors: {', '.join(self.available_doctors)}
Business hours: {self.business_hours['start']}:00 - {self.business_hours['end']}:00, {', '.join(self.business_hours['days'])}

Previous conversation:
{context}

Current user message: {transcript}

Available appointment slots: {available_times[:5]}  # Show next 5 available slots

Instructions:
1. For appointment booking, collect: patient name, preferred date/time, reason for visit, doctor preference
2. Suggest available time slots if user's preference isn't available
3. Be professional, empathetic, and helpful
4. Keep responses conversational but informative (under 150 words)
5. For urgent medical concerns, suggest contacting emergency services
6. Validate appointment details before confirming

Respond professionally and helpfully."""

            response = self.gemini_model.generate_content(prompt)
            ai_response = response.text.strip()
            
            # Update conversation context
            self.conversation_context.append({
                'user': transcript,
                'ai': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 5 exchanges
            self.conversation_context = self.conversation_context[-5:]
            
            # Extract intent and entities
            intent_data = await self.extract_intent(transcript, ai_response)
            
            return {
                'response': ai_response,
                'intent': intent_data.get('intent', 'general'),
                'entities': intent_data.get('entities', {}),
                'confidence': intent_data.get('confidence', 0.5),
                'suggestions': intent_data.get('suggestions', []),
                'urgency': intent_data.get('urgency', 'low')
            }
            
        except Exception as e:
            logger.error(f"Gemini response error: {str(e)}")
            raise Exception(f"AI response generation failed: {str(e)}")

    def _get_available_time_slots(self) -> list:
        """Generate available appointment time slots"""
        slots = []
        current_date = datetime.now().replace(hour=self.business_hours['start'], minute=0, second=0, microsecond=0)
        
        for day in range(14):  # Next 2 weeks
            check_date = current_date + timedelta(days=day)
            if check_date.strftime('%A').lower() in self.business_hours['days']:
                for hour in range(self.business_hours['start'], self.business_hours['end']):
                    for minute in [0, 30]:  # 30-minute slots
                        slot_time = check_date.replace(hour=hour, minute=minute)
                        if slot_time > datetime.now():
                            slots.append(slot_time.strftime('%Y-%m-%d %H:%M'))
        
        return slots[:20]  # Return next 20 available slots

    async def extract_intent(self, user_text: str, ai_response: str = "") -> Dict[str, Any]:
        """Extract intent and entities with enhanced accuracy"""
        if not self.gemini_model:
            return {
                'intent': 'general',
                'entities': {},
                'confidence': 0.3,
                'suggestions': [],
                'urgency': 'low'
            }
        
        try:
            intent_prompt = f"""
            Analyze this conversation for medical appointment management:
            
            User: "{user_text}"
            AI Response: "{ai_response}"
            
            Available doctors: {', '.join(self.available_doctors)}
            
            Return JSON with:
            {{
                "intent": "book_appointment" | "cancel_appointment" | "reschedule_appointment" | "check_availability" | "inquiry" | "emergency" | "general",
                "entities": {{
                    "patient_name": "extracted name or null",
                    "date": "YYYY-MM-DD or null", 
                    "time": "HH:MM or null",
                    "doctor": "doctor name or null",
                    "reason": "medical reason or null",
                    "phone": "phone number or null"
                }},
                "confidence": 0.0-1.0,
                "suggestions": ["list of helpful suggestions"],
                "urgency": "low" | "medium" | "high" | "emergency"
            }}
            
            Only return valid JSON, nothing else.
            """
            
            response = self.gemini_model.generate_content(intent_prompt)
            response_text = response.text.strip()
            
            # Clean the response to ensure it's valid JSON
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Try to parse JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}, Response: {response_text}")
                # Return a safe default
                result = {
                    'intent': 'general',
                    'entities': {},
                    'confidence': 0.3,
                    'suggestions': [],
                    'urgency': 'low'
                }
            
            # Clean and validate entities
            if result.get('entities'):
                entities = result['entities']
                # Validate date format
                if entities.get('date'):
                    try:
                        datetime.strptime(entities['date'], '%Y-%m-%d')
                    except ValueError:
                        entities['date'] = None
                
                # Validate doctor name
                if entities.get('doctor') and entities['doctor'] not in self.available_doctors:
                    # Try to match partial names
                    for doc in self.available_doctors:
                        if entities['doctor'].lower() in doc.lower():
                            entities['doctor'] = doc
                            break
                    else:
                        entities['doctor'] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Intent extraction error: {str(e)}")
            return {
                'intent': 'general', 
                'entities': {}, 
                'confidence': 0.3,
                'suggestions': [],
                'urgency': 'low'
            }

    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech with enhanced fallback handling"""
        if not ELEVENLABS_AVAILABLE:
            logger.warning("ElevenLabs not available, returning empty audio")
            return b""
        
        if not settings.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not provided, returning empty audio")
            return b""
        
        try:
            # Clean text for better speech synthesis
            clean_text = self._clean_text_for_speech(text)
            
            if generate:
                # Classic API
                audio = generate(
                    text=clean_text,
                    voice=settings.elevenlabs_voice_id,
                    model="eleven_monolingual_v1"
                )
                return audio if isinstance(audio, bytes) else b""
            elif self.elevenlabs_client:
                # New API
                try:
                    audio = self.elevenlabs_client.generate(
                        text=clean_text,
                        voice=settings.elevenlabs_voice_id,
                        model="eleven_monolingual_v1"
                    )
                    return audio if isinstance(audio, bytes) else b""
                except Exception as e:
                    logger.error(f"ElevenLabs new API error: {e}")
                    return b""
            else:
                logger.warning("No ElevenLabs method available")
                return b""
                
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {str(e)}")
            return b""  # Return empty audio instead of raising exception
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Handle common medical abbreviations
        replacements = {
            'Dr.': 'Doctor',
            'appt': 'appointment',
            'w/': 'with',
            'b/c': 'because',
            'etc.': 'etcetera'
        }
        
        for abbrev, full in replacements.items():
            text = text.replace(abbrev, full)
        
        return text

    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """Complete voice processing pipeline with enhanced error handling"""
        try:
            # Handle empty audio
            if not audio_data or len(audio_data) == 0:
                return {
                    'transcript': '',
                    'response': 'I couldn\'t hear you clearly. Could you please speak a bit louder or closer to the microphone?',
                    'audio': None,
                    'intent': 'general',
                    'entities': {},
                    'suggestions': ['Try speaking more clearly', 'Check your microphone'],
                    'urgency': 'low'
                }
            
            # Transcribe
            transcript = await self.transcribe_audio(audio_data)
            if not transcript.strip():
                return {
                    'transcript': '',
                    'response': 'I couldn\'t understand what you said. Please try speaking more clearly.',
                    'audio': None,
                    'intent': 'general',
                    'entities': {},
                    'suggestions': ['Speak more clearly', 'Check microphone volume'],
                    'urgency': 'low'
                }
            
            logger.info(f"Transcribed: {transcript}")
            
            # Generate AI response
            ai_data = await self.generate_response(transcript)
            
            # Generate speech
            audio_b64 = None
            try:
                audio = await self.text_to_speech(ai_data['response'])
                if audio:
                    audio_b64 = base64.b64encode(audio).decode('utf-8')
            except Exception as tts_error:
                logger.error(f"TTS failed: {tts_error}")
                audio_b64 = None
            
            return {
                'transcript': transcript,
                'response': ai_data['response'],
                'audio': audio_b64,
                'intent': ai_data['intent'],
                'entities': ai_data['entities'],
                'confidence': ai_data['confidence'],
                'suggestions': ai_data.get('suggestions', []),
                'urgency': ai_data.get('urgency', 'low')
            }
            
        except Exception as e:
            logger.error(f"Voice processing error: {str(e)}")
            error_response = 'I\'m sorry, I\'m experiencing technical difficulties. Please try again in a moment or contact our office directly.'
            
            try:
                error_audio = await self.text_to_speech(error_response)
                error_audio_b64 = base64.b64encode(error_audio).decode('utf-8') if error_audio else None
            except:
                error_audio_b64 = None
            
            return {
                'transcript': '',
                'response': error_response,
                'audio': error_audio_b64,
                'intent': 'error',
                'entities': {},
                'error': str(e),
                'suggestions': ['Try again', 'Contact office directly', 'Check internet connection'],
                'urgency': 'low'
            }

    async def process_audio_stream(self, audio_data: bytes) -> Dict[str, Any]:
        """Process incoming audio stream through the voice pipeline (backward compatibility)"""
        result = await self.process_voice_input(audio_data)
        return {
            "transcript": result['transcript'],
            "ai_response": {
                "text": result['response'],
                "intent": result['intent'],
                "extracted_info": result['entities']
            },
            "audio_response": result['audio'],
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": result.get('suggestions', []),
            "urgency": result.get('urgency', 'low')
        }

    def reset_conversation(self):
        """Reset conversation context"""
        self.conversation_context = []
        logger.info("Conversation context reset")
    
    def get_conversation_history(self) -> list:
        """Get current conversation history"""
        return self.conversation_context.copy()

    def health_check(self) -> Dict[str, Any]:
        """Check health of all voice service components"""
        health = {
            "deepgram": "unavailable",
            "gemini": "unavailable", 
            "elevenlabs": "unavailable"
        }
        
        if self.deepgram and settings.deepgram_api_key:
            health["deepgram"] = "available"
        
        if self.gemini_model and settings.gemini_api_key:
            health["gemini"] = "available"
            
        if ELEVENLABS_AVAILABLE and settings.elevenlabs_api_key:
            health["elevenlabs"] = "available"
        
        return health

# Global instance
voice_service = VoiceService()