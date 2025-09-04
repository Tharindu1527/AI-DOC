from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Appointment(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    patient_name: str = Field(..., description="Patient full name")
    patient_phone: Optional[str] = Field(None, description="Patient phone number")
    patient_email: Optional[str] = Field(None, description="Patient email address")
    doctor_name: str = Field(..., description="Doctor name")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(default=30, description="Appointment duration in minutes")
    status: str = Field(default="scheduled", description="Appointment status")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class AppointmentCreate(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    patient_name: str = Field(..., description="Patient full name")
    patient_phone: Optional[str] = Field(None, description="Patient phone number")
    patient_email: Optional[str] = Field(None, description="Patient email address")
    doctor_name: str = Field(..., description="Doctor name")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(default=30, description="Appointment duration in minutes")
    status: str = Field(default="scheduled", description="Appointment status")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")

class AppointmentUpdate(BaseModel):
    patient_name: Optional[str] = Field(None, description="Patient full name")
    patient_phone: Optional[str] = Field(None, description="Patient phone number")
    patient_email: Optional[str] = Field(None, description="Patient email address")
    doctor_name: Optional[str] = Field(None, description="Doctor name")
    appointment_date: Optional[datetime] = Field(None, description="Appointment date and time")
    duration_minutes: Optional[int] = Field(None, description="Appointment duration in minutes")
    status: Optional[str] = Field(None, description="Appointment status")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")

class AppointmentResponse(BaseModel):
    id: str = Field(..., description="Appointment ID")
    patient_id: str = Field(..., description="Patient ID")
    patient_name: str = Field(..., description="Patient full name")
    patient_phone: Optional[str] = Field(None, description="Patient phone number")
    patient_email: Optional[str] = Field(None, description="Patient email address")
    doctor_name: str = Field(..., description="Doctor name")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(..., description="Appointment duration in minutes")
    status: str = Field(..., description="Appointment status")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)