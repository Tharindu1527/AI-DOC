from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from services.doctor_service import doctor_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/doctors", tags=["doctors"])

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

@router.post("/", response_model=DoctorResponse)
async def create_doctor(doctor: DoctorCreate):
    """Create a new doctor"""
    try:
        result = await doctor_service.create_doctor(doctor)
        return result
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        raise HTTPException(status_code=500, detail="Failed to create doctor")

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

@router.get("/search/", response_model=List[DoctorResponse])
async def search_doctors(
    q: str = Query("", description="Search query"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    department: Optional[str] = Query(None, description="Filter by department"),
    min_experience: Optional[int] = Query(None, ge=0, description="Minimum years of experience")
):
    """Search doctors with filters"""
    try:
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active
        if is_available is not None:
            filters['is_available'] = is_available
        if specialty:
            filters['specialty'] = specialty
        if department:
            filters['department'] = department
        if min_experience:
            filters['min_experience'] = min_experience
            
        result = await doctor_service.search_doctors(query=q, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Error searching doctors: {e}")
        raise HTTPException(status_code=500, detail="Failed to search doctors")

@router.get("/statistics/", response_model=dict)
async def get_doctor_statistics():
    """Get doctor statistics for dashboard"""
    try:
        result = await doctor_service.get_doctor_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting doctor statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get doctor statistics")

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
