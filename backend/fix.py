#!/usr/bin/env python3
"""
Quick fix script to resolve FastAPI route ordering issues
Run this from the backend directory: python quick_fix.py
"""
import os
import sys

def fix_appointments_api():
    """Fix appointments API route ordering"""
    content = '''from datetime import datetime, date
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
'''

    with open('api/appointments.py', 'w') as f:
        f.write(content)
    print("✅ Fixed appointments.py")

def fix_patients_api():
    """Fix patients API route ordering"""
    content = '''from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.patient import PatientCreate, PatientUpdate, PatientResponse
from services.patient_service import patient_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])

# SPECIFIC ROUTES FIRST
@router.get("/statistics/", response_model=dict)
async def get_patient_statistics():
    """Get patient statistics for dashboard"""
    try:
        result = await patient_service.get_patient_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting patient statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient statistics")

@router.get("/search/", response_model=List[PatientResponse])
async def search_patients(
    q: str = Query("", description="Search query"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    age_min: Optional[int] = Query(None, description="Minimum age"),
    age_max: Optional[int] = Query(None, description="Maximum age"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Search patients with filters"""
    try:
        filters = {}
        if gender:
            filters['gender'] = gender
        if age_min is not None:
            filters['age_min'] = age_min
        if age_max is not None:
            filters['age_max'] = age_max
        if is_active is not None:
            filters['is_active'] = is_active
            
        result = await patient_service.search_patients(query=q, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to search patients")

@router.get("/find/by-name-phone", response_model=PatientResponse)
async def find_patient_by_name_phone(
    name: Optional[str] = Query(None, description="Patient name"),
    phone: Optional[str] = Query(None, description="Patient phone number")
):
    """Find patient by name or phone (for voice appointments)"""
    try:
        if not name and not phone:
            raise HTTPException(status_code=400, detail="Either name or phone is required")
            
        result = await patient_service.get_patient_by_name_phone(name=name, phone=phone)
        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to find patient")

@router.get("/", response_model=List[PatientResponse])
async def get_all_patients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    active_only: bool = Query(True, description="Return only active patients")
):
    """Get all patients with pagination"""
    try:
        result = await patient_service.get_all_patients(skip=skip, limit=limit, active_only=active_only)
        return result
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patients")

@router.post("/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate):
    """Create a new patient"""
    try:
        result = await patient_service.create_patient(patient)
        return result
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to create patient")

# PARAMETERIZED ROUTES LAST
@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    """Get patient by ID"""
    try:
        result = await patient_service.get_patient(patient_id)
        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient")

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: str, update_data: PatientUpdate):
    """Update a patient"""
    try:
        result = await patient_service.update_patient(patient_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to update patient")

@router.delete("/{patient_id}")
async def deactivate_patient(patient_id: str):
    """Deactivate a patient (soft delete)"""
    try:
        success = await patient_service.deactivate_patient(patient_id)
        if not success:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"message": "Patient deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate patient")
'''

    with open('api/patients.py', 'w') as f:
        f.write(content)
    print("✅ Fixed patients.py")

def fix_doctors_api():
    """Fix doctors API route ordering"""
    content = '''from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from services.doctor_service import doctor_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/doctors", tags=["doctors"])

# SPECIFIC ROUTES FIRST
@router.get("/statistics/", response_model=dict)
async def get_doctor_statistics():
    """Get doctor statistics for dashboard"""
    try:
        result = await doctor_service.get_doctor_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting doctor statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get doctor statistics")

@router.get("/search/", response_model=List[DoctorResponse])
async def search_doctors(
    q: str = Query("", description="Search query"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    department: Optional[str] = Query(None, description="Filter by department"),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Search doctors with filters"""
    try:
        filters = {}
        if specialty:
            filters['specialty'] = specialty
        if department:
            filters['department'] = department
        if min_experience is not None:
            filters['min_experience'] = min_experience
        if is_available is not None:
            filters['is_available'] = is_available
        if is_active is not None:
            filters['is_active'] = is_active
            
        result = await doctor_service.search_doctors(query=q, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Error searching doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to search doctors")

@router.get("/available/", response_model=List[DoctorResponse])
async def get_available_doctors(
    specialty: Optional[str] = Query(None, description="Filter by specialty")
):
    """Get available doctors, optionally filtered by specialty"""
    try:
        result = await doctor_service.get_available_doctors(specialty=specialty)
        return result
    except Exception as e:
        logger.error(f"Error getting available doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available doctors")

@router.get("/find/by-name", response_model=DoctorResponse)
async def find_doctor_by_name(
    name: str = Query(..., description="Doctor name")
):
    """Find doctor by name (for voice appointments)"""
    try:
        result = await doctor_service.get_doctor_by_name(name)
        if not result:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding doctor: {e}")
        raise HTTPException(status_code=500, detail="Failed to find doctor")

@router.get("/", response_model=List[DoctorResponse])
async def get_all_doctors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    active_only: bool = Query(True, description="Return only active doctors")
):
    """Get all doctors with pagination"""
    try:
        result = await doctor_service.get_all_doctors(skip=skip, limit=limit, active_only=active_only)
        return result
    except Exception as e:
        logger.error(f"Error getting doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to get doctors")

@router.post("/", response_model=DoctorResponse)
async def create_doctor(doctor: DoctorCreate):
    """Create a new doctor"""
    try:
        result = await doctor_service.create_doctor(doctor)
        return result
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        raise HTTPException(status_code=500, detail="Failed to create doctor")

# PARAMETERIZED ROUTES LAST
@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: str):
    """Get doctor by ID"""
    try:
        result = await doctor_service.get_doctor(doctor_id)
        if not result:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting doctor: {e}")
        raise HTTPException(status_code=500, detail="Failed to get doctor")

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(doctor_id: str, update_data: DoctorUpdate):
    """Update a doctor"""
    try:
        result = await doctor_service.update_doctor(doctor_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating doctor: {e}")
        raise HTTPException(status_code=500, detail="Failed to update doctor")

@router.delete("/{doctor_id}")
async def deactivate_doctor(doctor_id: str):
    """Deactivate a doctor (soft delete)"""
    try:
        success = await doctor_service.deactivate_doctor(doctor_id)
        if not success:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return {"message": "Doctor deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating doctor: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate doctor")
'''

    with open('api/doctors.py', 'w') as f:
        f.write(content)
    print("✅ Fixed doctors.py")

def main():
    """Run all fixes"""
    print("🔧 Applying FastAPI route ordering fixes...")
    
    if not os.path.exists('api'):
        print("❌ Error: Run this script from the backend directory")
        sys.exit(1)
    
    try:
        fix_appointments_api()
        fix_patients_api()
        fix_doctors_api()
        
        print("\n🎉 All fixes applied successfully!")
        print("   Restart your backend server to apply changes:")
        print("   Ctrl+C to stop, then: python main.py")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()