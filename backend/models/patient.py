from datetime import datetime
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

class PatientBase(BaseModel):
    first_name: str = Field(..., description="Patient's first name")
    last_name: str = Field(..., description="Patient's last name")
    email: Optional[EmailStr] = Field(None, description="Patient's email address")
    phone: Optional[str] = Field(None, description="Patient's phone number")
    date_of_birth: Optional[datetime] = Field(None, description="Patient's date of birth")
    gender: Optional[str] = Field(None, description="Patient's gender")
    address: Optional[str] = Field(None, description="Patient's address")
    city: Optional[str] = Field(None, description="Patient's city")
    state: Optional[str] = Field(None, description="Patient's state")
    zip_code: Optional[str] = Field(None, description="Patient's ZIP code")
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    medical_history: Optional[List[str]] = Field(default_factory=list, description="Medical history")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Known allergies")
    medications: Optional[List[str]] = Field(default_factory=list, description="Current medications")
    insurance_provider: Optional[str] = Field(None, description="Insurance provider")
    insurance_id: Optional[str] = Field(None, description="Insurance ID number")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_active: bool = Field(default=True, description="Whether patient is active")

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class Patient(PatientBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    patient_id: str = Field(..., description="Unique patient identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> Optional[int]:
        if self.date_of_birth:
            today = datetime.now()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PatientResponse(BaseModel):
    id: str
    patient_id: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    medical_history: Optional[List[str]]
    allergies: Optional[List[str]]
    medications: Optional[List[str]]
    insurance_provider: Optional[str]
    insurance_id: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        if self.date_of_birth:
            today = datetime.now()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
