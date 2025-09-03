from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.patient import PatientCreate, PatientUpdate, PatientResponse
from services.patient_service import patient_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])

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

@router.post("/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate):
    """Create a new patient"""
    try:
        result = await patient_service.create_patient(patient)
        return result
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to create patient")

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

@router.get("/search/", response_model=List[PatientResponse])
async def search_patients(
    q: str = Query("", description="Search query"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    city: Optional[str] = Query(None, description="Filter by city"),
    age_from: Optional[int] = Query(None, ge=0, le=120, description="Minimum age"),
    age_to: Optional[int] = Query(None, ge=0, le=120, description="Maximum age")
):
    """Search patients with filters"""
    try:
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active
        if gender:
            filters['gender'] = gender
        if city:
            filters['city'] = city
        if age_from:
            filters['age_from'] = age_from
        if age_to:
            filters['age_to'] = age_to
            
        result = await patient_service.search_patients(query=q, filters=filters)
        return result
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to search patients")

@router.get("/statistics/", response_model=dict)
async def get_patient_statistics():
    """Get patient statistics for dashboard"""
    try:
        result = await patient_service.get_patient_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting patient statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient statistics")

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
