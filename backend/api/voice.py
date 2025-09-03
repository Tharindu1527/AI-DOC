import json
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from services.voice_service import voice_service
from services.appointment_service import appointment_service
from models.appointment import AppointmentCreate
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/process")
async def process_audio(audio_file: UploadFile = File(...)):
    """Process uploaded audio file through the enhanced voice pipeline"""
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file type")
        
        # Read audio file
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process through enhanced voice pipeline
        result = await voice_service.process_voice_input(audio_data)
        
        # Handle appointment actions if intent detected
        if result.get('intent') in ['book_appointment', 'cancel_appointment', 'reschedule_appointment']:
            appointment_result = await handle_appointment_action(result)
            result['appointment_action'] = appointment_result
        
        return {
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

async def handle_appointment_action(voice_result: dict) -> dict:
    """Handle appointment-related actions from voice input"""
    try:
        intent = voice_result.get('intent')
        entities = voice_result.get('entities', {})
        
        if intent == 'book_appointment':
            # Validate appointment data
            validation = appointment_service.validate_appointment_data(entities)
            
            if not validation['valid']:
                return {
                    'action': 'validation_failed',
                    'errors': validation['errors'],
                    'suggestions': validation['suggestions'],
                    'message': 'Please provide the missing information to complete your booking.'
                }
            
            # Create appointment
            booking_result = await appointment_service.create_appointment_from_voice(entities, voice_result)
            
            if booking_result['success']:
                return {
                    'action': 'appointment_created',
                    'appointment': booking_result['appointment'].dict(),
                    'message': booking_result['message']
                }
            else:
                return {
                    'action': 'booking_failed',
                    'message': booking_result['message'],
                    'available_slots': booking_result.get('available_slots', [])
                }
        
        elif intent == 'cancel_appointment':
            # Handle appointment cancellation
            if entities.get('patient_name'):
                appointments = await appointment_service.get_appointments_by_patient(entities['patient_name'])
                if appointments:
                    return {
                        'action': 'cancel_confirmation_needed',
                        'appointments': [apt.dict() for apt in appointments],
                        'message': 'Which appointment would you like to cancel?'
                    }
                else:
                    return {
                        'action': 'no_appointments_found',
                        'message': 'No appointments found for this patient.'
                    }
            else:
                return {
                    'action': 'patient_info_needed',
                    'message': 'Please provide the patient name to find appointments to cancel.'
                }
        
        elif intent == 'reschedule_appointment':
            # Handle appointment rescheduling
            return {
                'action': 'reschedule_info_needed',
                'message': 'To reschedule, please provide the current appointment details and your preferred new time.'
            }
        
        return {
            'action': 'no_action',
            'message': 'No specific appointment action required.'
        }
        
    except Exception as e:
        logger.error(f"Error handling appointment action: {e}")
        return {
            'action': 'error',
            'message': 'Sorry, there was an error processing your appointment request.',
            'error': str(e)
        }

@router.websocket("/stream")
async def voice_stream(websocket: WebSocket):
    """Real-time voice processing WebSocket endpoint"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("type") == "audio":
                # Decode base64 audio data
                audio_data = base64.b64decode(data["audio"])
                
                # Process through voice pipeline
                result = await voice_service.process_audio_stream(audio_data)
                
                # Handle appointment actions based on intent
                if result.get("ai_response", {}).get("intent") in ["book", "reschedule", "cancel"]:
                    appointment_result = await handle_appointment_action(result)
                    result["appointment_action"] = appointment_result
                
                # Send result back to client
                await websocket.send_text(json.dumps(result))
            
            elif data.get("type") == "reset":
                # Reset conversation context
                voice_service.reset_conversation()
                await websocket.send_text(json.dumps({"status": "conversation_reset"}))
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"error": str(e)}))

async def handle_appointment_action(voice_result: dict) -> dict:
    """Handle appointment booking, rescheduling, or cancellation based on voice intent"""
    try:
        ai_response = voice_result.get("ai_response", {})
        intent = ai_response.get("intent")
        extracted_info = ai_response.get("extracted_info", {})
        
        if intent == "book":
            return await handle_booking(extracted_info)
        elif intent == "reschedule":
            return await handle_reschedule(extracted_info)
        elif intent == "cancel":
            return await handle_cancellation(extracted_info)
        
        return {"status": "no_action", "message": "No appointment action required"}
        
    except Exception as e:
        logger.error(f"Error handling appointment action: {e}")
        return {"status": "error", "message": str(e)}

async def handle_booking(extracted_info: dict) -> dict:
    """Handle appointment booking"""
    try:
        # Extract required information
        patient_name = extracted_info.get("patient_name")
        doctor_name = extracted_info.get("doctor_name")
        date_str = extracted_info.get("date")
        time_str = extracted_info.get("time")
        
        if not all([patient_name, doctor_name, date_str, time_str]):
            return {
                "status": "incomplete_info",
                "message": "Missing required information for booking",
                "missing": [
                    field for field, value in {
                        "patient_name": patient_name,
                        "doctor_name": doctor_name,
                        "date": date_str,
                        "time": time_str
                    }.items() if not value
                ]
            }
        
        # Parse date and time
        try:
            if "tomorrow" in date_str.lower():
                appointment_date = datetime.now() + timedelta(days=1)
            elif "today" in date_str.lower():
                appointment_date = datetime.now()
            else:
                # Try to parse the date string
                appointment_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Parse time
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            appointment_date = appointment_date.replace(
                hour=time_obj.hour,
                minute=time_obj.minute,
                second=0,
                microsecond=0
            )
            
        except ValueError as e:
            return {
                "status": "invalid_datetime",
                "message": f"Invalid date or time format: {e}"
            }
        
        # Check availability
        available_slots = await appointment_service.get_available_slots(doctor_name, appointment_date)
        if appointment_date not in available_slots:
            return {
                "status": "slot_unavailable",
                "message": f"The requested time slot is not available",
                "available_slots": [slot.strftime("%H:%M") for slot in available_slots]
            }
        
        # Create appointment
        appointment_data = AppointmentCreate(
            patient_id=patient_name.lower().replace(" ", "_"),
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appointment_date,
            duration_minutes=30,
            status="scheduled"
        )
        
        result = await appointment_service.create_appointment(appointment_data)
        
        return {
            "status": "success",
            "message": "Appointment booked successfully",
            "appointment": {
                "id": result.id,
                "patient_name": result.patient_name,
                "doctor_name": result.doctor_name,
                "date": result.appointment_date.isoformat(),
                "status": result.status
            }
        }
        
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        return {"status": "error", "message": str(e)}

async def handle_reschedule(extracted_info: dict) -> dict:
    """Handle appointment rescheduling"""
    try:
        # This would require appointment ID or patient details to find existing appointment
        # For demo purposes, return a placeholder response
        return {
            "status": "not_implemented",
            "message": "Rescheduling functionality requires appointment identification"
        }
    except Exception as e:
        logger.error(f"Error rescheduling appointment: {e}")
        return {"status": "error", "message": str(e)}

async def handle_cancellation(extracted_info: dict) -> dict:
    """Handle appointment cancellation"""
    try:
        # This would require appointment ID or patient details to find existing appointment
        # For demo purposes, return a placeholder response
        return {
            "status": "not_implemented",
            "message": "Cancellation functionality requires appointment identification"
        }
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/conversation")
async def get_conversation_history():
    """Get current conversation history"""
    try:
        history = voice_service.get_conversation_history()
        return {"conversation": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history")

@router.post("/conversation/reset")
async def reset_conversation():
    """Reset conversation context"""
    try:
        voice_service.reset_conversation()
        return {"message": "Conversation reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation") 