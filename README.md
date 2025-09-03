# DocTalk AI - Real-Time GP Booking Voice Agent

## Overview
DocTalk AI is a real-time conversational GP booking assistant that uses voice interaction powered by Deepgram for speech recognition, Google's Gemini 1.5 Flash for natural language processing, and ElevenLabs for text-to-speech synthesis.

## Features

### Core Features
- **Real-Time Voice Pipeline**: Microphone/WebRTC input streamed to Deepgram for live transcription; GPT-4o-mini for intent; ElevenLabs for real-time TTS
- **MongoDB Appointment System**: Store patient bookings with fields such as patientId, name, doctor, date, time, status
- **Backend (Python FastAPI)**: REST APIs + WebSocket for real-time voice handling and appointment updates
- **Frontend (React.js)**: UI for live transcript, microphone button, and AI voice playback

### Implementation Steps
1. **Real-Time STT**: Integrate Deepgram streaming API to transcribe user audio in real-time
2. **Intent Processing**: Send transcripts to Gemini 1.5 Flash to detect intent (book/reschedule/cancel/query)
3. **Real-Time TTS**: Use ElevenLabs streaming API to generate natural voice output while GPT responds
4. **MongoDB Appointment System**: Implement schema and CRUD APIs for appointments
5. **Demo Conversation**: Full voice-to-voice booking flow (book, reschedule, cancel)

### Stretch Goals (Optional)
- Support barge-in (interruptions while the agent is speaking)
- Add patient authentication (via ID or phone number)
- Sync appointments with Google Calendar API
- Deploy backend on a WebSocket-enabled cloud server

## Tech Stack
- **Frontend**: React.js with TypeScript, Tailwind CSS, Framer Motion
- **Backend**: Python FastAPI with WebSocket support
- **Database**: MongoDB
- **APIs**: Deepgram (STT), Gemini 1.5 Flash (LLM), ElevenLabs (TTS)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- MongoDB
- API Keys for Deepgram, Google AI Studio (Gemini), and ElevenLabs

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doctalk-ai
```

2. Set up the backend:
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python main.py
```

3. Set up the frontend:
```bash
cd frontend
npm install
npm start
```

### Environment Variables

Backend (.env):
```
DEEPGRAM_API_KEY=your_deepgram_key
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
MONGODB_URL=mongodb://localhost:27017/doctalk
```

## Project Structure
```
doctalk-ai/
├── backend/           # Python FastAPI backend
├── frontend/          # React.js frontend
└── README.md
```

## Example Conversation Flow
```
Patient: "I want to see Dr. Smith tomorrow morning."
DocTalk AI: "Sure, tomorrow 10 AM is available. Should I book it for you?"
Patient: "Yes, please."
DocTalk AI: "Done, your appointment with Dr. Smith is confirmed for tomorrow at 10 AM."
```

## Evaluation Criteria
- ✅ Working real-time speech-to-speech pipeline (Deepgram → Gemini → ElevenLabs)
- ✅ MongoDB integrated with CRUD operations for appointments
- ✅ Successful demo of booking, rescheduling, and cancelling appointments
- ✅ Clean and maintainable code with documentation
- ✅ Frontend demo for user interaction 