import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any, Optional
import google.generativeai as genai
from deepgram import Deepgram
from elevenlabs import generate, set_api_key
import httpx
from config import settings
import logging
import re

logger = logging.getLogger(__name__)

# Configure APIs
genai.configure(api_key=settings.gemini_api_key)
set_api_key(settings.elevenlabs_api_key)

class VoiceService:
    def __init__(self):
        self.deepgram = Deepgram(settings.deepgram_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
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
        try:
            response = await self.deepgram.transcription.prerecorded(
                {'buffer': audio_data, 'mimetype': 'audio/wav'},
                {
                    'punctuate': True, 
                    'language': 'en',
                    'model': 'nova-2',
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
                'suggestions': intent_data.get('suggestions', [])
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
            result = json.loads(response.text.strip())
            
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
        """Convert text to speech with enhanced settings"""
        try:
            # Clean text for better speech synthesis
            clean_text = self._clean_text_for_speech(text)
            
            audio = generate(
                text=clean_text,
                voice=settings.elevenlabs_voice_id,
                model="eleven_monolingual_v1",
                settings={
                    "stability": 0.7,
                    "similarity_boost": 0.8,
                    "style": 0.1,
                    "use_speaker_boost": True
                }
            )
            return audio
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {str(e)}")
            raise Exception(f"Text-to-speech conversion failed: {str(e)}")
    
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
            # Transcribe
            transcript = await self.transcribe_audio(audio_data)
            if not transcript.strip():
                return {
                    'transcript': '',
                    'response': 'I couldn\'t hear you clearly. Could you please speak a bit louder or closer to the microphone?',
                    'audio': None,
                    'intent': 'general',
                    'entities': {},
                    'suggestions': ['Try speaking more clearly', 'Check your microphone']
                }
            
            logger.info(f"Transcribed: {transcript}")
            
            # Generate AI response
            ai_data = await self.generate_response(transcript)
            
            # Generate speech
            try:
                audio = await self.text_to_speech(ai_data['response'])
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
                error_audio_b64 = base64.b64encode(error_audio).decode('utf-8')
            except:
                error_audio_b64 = None
            
            return {
                'transcript': '',
                'response': error_response,
                'audio': error_audio_b64,
                'intent': 'error',
                'entities': {},
                'error': str(e),
                'suggestions': ['Try again', 'Contact office directly', 'Check internet connection']
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
            "timestamp": datetime.utcnow().isoformat()
        }

    async def process_realtime_audio(self, websocket) -> AsyncGenerator[Dict[str, Any], None]:
        """Process real-time audio stream"""
        try:
            while True:
                # Receive audio data from WebSocket
                audio_data = await websocket.receive_bytes()
                
                # Process through voice pipeline
                result = await self.process_audio_stream(audio_data)
                
                # Yield result
                yield result
                
        except Exception as e:
            logger.error(f"Real-time audio processing error: {e}")
            yield {"error": str(e)}

    def reset_conversation(self):
        """Reset conversation context"""
        self.conversation_context = []
        logger.info("Conversation context reset")
    
    def get_conversation_history(self) -> list:
        """Get current conversation history"""
        return self.conversation_context.copy()

# Global instance
voice_service = VoiceService()
