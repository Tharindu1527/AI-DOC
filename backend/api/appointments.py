from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from services.appointment_service import appointment_service
from database.mongodb import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["appointments"])

# SPECIFIC ROUTES FIRST - before parameterized routes
@router.get("/statistics/", response_model=dict)
async def get_appointment_statistics():
    """Get appointment statistics for dashboard"""
    try:
        result = await appointment_service.get_appointment_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting appointment statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get appointment statistics")

@router.get("/search/", response_model=List[AppointmentResponse])
async def search_appointments(
    q: str = Query("", description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    doctor: Optional[str] = Query(None, description="Filter by doctor"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)")
):
    """Search appointments with filters"""
    try:
        filters = {}
        if status:
            filters['status'] = status
        if doctor:
            filters['doctor'] = doctor
        if date_from:
            filters['date_from'] = datetime.combine(date_from, datetime.min.time())
        if date_to:
            filters['date_to'] = datetime.combine(date_to, datetime.max.time())
            
        result = await appointment_service.search_appointments(query=q, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Error searching appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to search appointments")

@router.get("/all/", response_model=List[AppointmentResponse])
async def get_all_appointments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    include_cancelled: bool = Query(False, description="Include cancelled appointments")
):
    """Get all appointments with pagination"""
    try:
        db = get_database()
        query = {}
        if not include_cancelled:
            query["status"] = {"$ne": "cancelled"}
        
        cursor = db["appointments"].find(query).skip(skip).limit(limit).sort("appointment_date", -1)
        appointments = await cursor.to_list(length=limit)
        
        result = []
        for appointment in appointments:
            result.append(AppointmentResponse(
                id=str(appointment["_id"]),
                **{k: v for k, v in appointment.items() if k != "_id"}
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error getting all appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get appointments")

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment"""
    try:
        result = await appointment_service.create_appointment(appointment)
        return result
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment")

# PARAMETERIZED ROUTES LAST
@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    """Get appointment by ID"""
    try:
        result = await appointment_service.get_appointment(appointment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to get appointment")

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
async def get_patient_appointments(patient_id: str):
    """Get all appointments for a patient"""
    try:
        result = await appointment_service.get_appointments_by_patient(patient_id)
        return result
    except Exception as e:
        logger.error(f"Error getting patient appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient appointments")

@router.get("/doctor/{doctor_name}", response_model=List[AppointmentResponse])
async def get_doctor_appointments(
    doctor_name: str,
    date: Optional[date] = Query(None, description="Filter by specific date (YYYY-MM-DD)")
):
    """Get appointments for a doctor, optionally filtered by date"""
    try:
        filter_date = None
        if date:
            filter_date = datetime.combine(date, datetime.min.time())
        
        result = await appointment_service.get_appointments_by_doctor(doctor_name, filter_date)
        return result
    except Exception as e:
        logger.error(f"Error getting doctor appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get doctor appointments")

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, update_data: AppointmentUpdate):
    """Update an appointment"""
    try:
        result = await appointment_service.update_appointment(appointment_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")

@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment"""
    try:
        result = await appointment_service.cancel_appointment(appointment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return {"message": "Appointment cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")

@router.get("/availability/{doctor_name}")
async def get_available_slots(
    doctor_name: str,
    date: date = Query(..., description="Date to check availability (YYYY-MM-DD)")
):
    """Get available time slots for a doctor on a specific date"""
    try:
        check_date = datetime.combine(date, datetime.min.time())
        slots = await appointment_service.get_available_slots(doctor_name, check_date)
        
        # Format slots for frontend
        formatted_slots = [slot.strftime("%H:%M") for slot in slots]
        
        return {
            "doctor": doctor_name,
            "date": date.isoformat(),
            "available_slots": formatted_slots
        }
    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available slots")
