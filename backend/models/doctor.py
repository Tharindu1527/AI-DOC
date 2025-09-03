from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
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

class WorkingHours(BaseModel):
    day: str = Field(..., description="Day of the week")
    start_time: time = Field(..., description="Start time")
    end_time: time = Field(..., description="End time")
    is_available: bool = Field(default=True, description="Whether doctor is available on this day")

class DoctorBase(BaseModel):
    first_name: str = Field(..., description="Doctor's first name")
    last_name: str = Field(..., description="Doctor's last name")
    title: str = Field(default="Dr.", description="Doctor's title (Dr., Prof., etc.)")
    specialty: str = Field(..., description="Doctor's medical specialty")
    department: Optional[str] = Field(None, description="Department or clinic")
    email: Optional[EmailStr] = Field(None, description="Doctor's email address")
    phone: Optional[str] = Field(None, description="Doctor's phone number")
    office_location: Optional[str] = Field(None, description="Office location or room number")
    education: Optional[List[str]] = Field(default_factory=list, description="Educational background")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Medical certifications")
    years_experience: Optional[int] = Field(None, description="Years of medical experience")
    languages: Optional[List[str]] = Field(default_factory=list, description="Languages spoken")
    bio: Optional[str] = Field(None, description="Doctor's biography")
    consultation_fee: Optional[float] = Field(None, description="Consultation fee")
    working_hours: Optional[List[WorkingHours]] = Field(default_factory=list, description="Weekly working hours")
    is_available: bool = Field(default=True, description="Whether doctor is currently available for appointments")
    is_active: bool = Field(default=True, description="Whether doctor is active in the system")
    rating: Optional[float] = Field(None, description="Doctor's average rating")
    total_reviews: int = Field(default=0, description="Total number of reviews")

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    specialty: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    office_location: Optional[str] = None
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    years_experience: Optional[int] = None
    languages: Optional[List[str]] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None
    working_hours: Optional[List[WorkingHours]] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    rating: Optional[float] = None
    total_reviews: Optional[int] = None

class Doctor(DoctorBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    doctor_id: str = Field(..., description="Unique doctor identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def full_name(self) -> str:
        return f"{self.title} {self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        return f"{self.title} {self.last_name}"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DoctorResponse(BaseModel):
    id: str
    doctor_id: str
    first_name: str
    last_name: str
    title: str
    specialty: str
    department: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    office_location: Optional[str]
    education: Optional[List[str]]
    certifications: Optional[List[str]]
    years_experience: Optional[int]
    languages: Optional[List[str]]
    bio: Optional[str]
    consultation_fee: Optional[float]
    working_hours: Optional[List[WorkingHours]]
    is_available: bool
    is_active: bool
    rating: Optional[float]
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        return f"{self.title} {self.first_name} {self.last_name}"
    
    @property
    def display_name(self) -> str:
        return f"{self.title} {self.last_name}"
