from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class AppointmentBase(BaseModel):
    patient_id: str = Field(..., description="Patient ID or identifier")
    patient_name: str = Field(..., description="Patient's full name")
    patient_phone: Optional[str] = Field(None, description="Patient's phone number")
    doctor_name: str = Field(..., description="Doctor's name")
    appointment_date: datetime = Field(..., description="Date and time of appointment")
    duration_minutes: int = Field(default=30, description="Duration in minutes")
    status: str = Field(default="scheduled", description="Appointment status")
    notes: Optional[str] = Field(None, description="Additional notes")

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    doctor_name: Optional[str] = None
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class Appointment(AppointmentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    patient_phone: Optional[str]
    doctor_name: str
    appointment_date: datetime
    duration_minutes: int
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime 