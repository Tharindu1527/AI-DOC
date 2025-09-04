#!/usr/bin/env python3
"""
Create sample data for DocTalk AI
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, time, date
import random

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import connect_to_mongo, close_mongo_connection, get_database
from models.doctor import Doctor, WorkingHours
from models.patient import Patient
from models.appointment import Appointment

# Sample data
DOCTORS_DATA = [
    {
        "first_name": "John", "last_name": "Smith", "specialty": "General Practice",
        "department": "Family Medicine", "years_experience": 15,
        "email": "j.smith@hospital.com", "phone": "+1-555-0101"
    },
    {
        "first_name": "Sarah", "last_name": "Johnson", "specialty": "Cardiology",
        "department": "Cardiology", "years_experience": 12,
        "email": "s.johnson@hospital.com", "phone": "+1-555-0102"
    },
    {
        "first_name": "Michael", "last_name": "Williams", "specialty": "Pediatrics",
        "department": "Pediatrics", "years_experience": 8,
        "email": "m.williams@hospital.com", "phone": "+1-555-0103"
    },
    {
        "first_name": "Emily", "last_name": "Brown", "specialty": "Dermatology",
        "department": "Dermatology", "years_experience": 10,
        "email": "e.brown@hospital.com", "phone": "+1-555-0104"
    },
    {
        "first_name": "David", "last_name": "Davis", "specialty": "Orthopedics",
        "department": "Orthopedics", "years_experience": 18,
        "email": "d.davis@hospital.com", "phone": "+1-555-0105"
    },
    {
        "first_name": "Lisa", "last_name": "Miller", "specialty": "Neurology",
        "department": "Neurology", "years_experience": 14,
        "email": "l.miller@hospital.com", "phone": "+1-555-0106"
    },
    {
        "first_name": "James", "last_name": "Wilson", "specialty": "Oncology",
        "department": "Oncology", "years_experience": 20,
        "email": "j.wilson@hospital.com", "phone": "+1-555-0107"
    },
    {
        "first_name": "Jennifer", "last_name": "Moore", "specialty": "Psychiatry",
        "department": "Mental Health", "years_experience": 11,
        "email": "j.moore@hospital.com", "phone": "+1-555-0108"
    }
]

PATIENTS_DATA = [
    {
        "first_name": "Alice", "last_name": "Cooper", "email": "alice.cooper@email.com",
        "phone": "+1-555-1001", "gender": "female", "city": "New York", "state": "NY"
    },
    {
        "first_name": "Bob", "last_name": "Anderson", "email": "bob.anderson@email.com",
        "phone": "+1-555-1002", "gender": "male", "city": "Los Angeles", "state": "CA"
    },
    {
        "first_name": "Carol", "last_name": "Thomas", "email": "carol.thomas@email.com",
        "phone": "+1-555-1003", "gender": "female", "city": "Chicago", "state": "IL"
    },
    {
        "first_name": "Daniel", "last_name": "Jackson", "email": "daniel.jackson@email.com",
        "phone": "+1-555-1004", "gender": "male", "city": "Houston", "state": "TX"
    },
    {
        "first_name": "Eva", "last_name": "White", "email": "eva.white@email.com",
        "phone": "+1-555-1005", "gender": "female", "city": "Phoenix", "state": "AZ"
    },
    {
        "first_name": "Frank", "last_name": "Harris", "email": "frank.harris@email.com",
        "phone": "+1-555-1006", "gender": "male", "city": "Philadelphia", "state": "PA"
    },
    {
        "first_name": "Grace", "last_name": "Martin", "email": "grace.martin@email.com",
        "phone": "+1-555-1007", "gender": "female", "city": "San Antonio", "state": "TX"
    },
    {
        "first_name": "Henry", "last_name": "Thompson", "email": "henry.thompson@email.com",
        "phone": "+1-555-1008", "gender": "male", "city": "San Diego", "state": "CA"
    },
    {
        "first_name": "Isabella", "last_name": "Garcia", "email": "isabella.garcia@email.com",
        "phone": "+1-555-1009", "gender": "female", "city": "Dallas", "state": "TX"
    },
    {
        "first_name": "Jack", "last_name": "Rodriguez", "email": "jack.rodriguez@email.com",
        "phone": "+1-555-1010", "gender": "male", "city": "San Jose", "state": "CA"
    }
]

def generate_doctor_id():
    """Generate a unique doctor ID"""
    return f"D{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_patient_id():
    """Generate a unique patient ID"""
    return f"P{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def create_default_working_hours():
    """Create default working hours (9 AM - 5 PM, Monday-Friday)"""
    return [
        WorkingHours(day="Monday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Tuesday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Wednesday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Thursday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Friday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Saturday", start_time=time(9, 0), end_time=time(13, 0), is_available=False),
        WorkingHours(day="Sunday", start_time=time(9, 0), end_time=time(13, 0), is_available=False)
    ]

async def create_doctors():
    """Create sample doctors"""
    print("Creating sample doctors...")
    db = get_database()
    
    doctors = []
    for doctor_data in DOCTORS_DATA:
        doctor = Doctor(
            doctor_id=generate_doctor_id(),
            working_hours=create_default_working_hours(),
            languages=["English"],
            consultation_fee=random.choice([150.0, 200.0, 250.0, 300.0]),
            rating=round(random.uniform(4.0, 5.0), 1),
            total_reviews=random.randint(50, 500),
            **doctor_data
        )
        doctors.append(doctor.dict(by_alias=True))
    
    result = await db.doctors.insert_many(doctors)
    print(f"Created {len(result.inserted_ids)} doctors")
    return result.inserted_ids

async def create_patients():
    """Create sample patients"""
    print("Creating sample patients...")
    db = get_database()
    
    patients = []
    for patient_data in PATIENTS_DATA:
        # Generate random date of birth (between 18-80 years old)
        birth_year = random.randint(datetime.now().year - 80, datetime.now().year - 18)
        birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        patient = Patient(
            patient_id=generate_patient_id(),
            date_of_birth=birth_date,
            address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'First St', 'Park Rd'])}",
            zip_code=f"{random.randint(10000, 99999)}",
            allergies=random.choice([[], ["Penicillin"], ["Peanuts"], ["Latex", "Shellfish"]]),
            medications=random.choice([[], ["Aspirin"], ["Lisinopril"], ["Metformin", "Atorvastatin"]]),
            insurance_provider=random.choice(["Blue Cross", "Aetna", "Cigna", "United Health"]),
            **patient_data
        )
        patients.append(patient.dict(by_alias=True))
    
    result = await db.patients.insert_many(patients)
    print(f"Created {len(result.inserted_ids)} patients")
    return result.inserted_ids

async def create_appointments():
    """Create sample appointments"""
    print("Creating sample appointments...")
    db = get_database()
    
    # Get created doctors and patients
    doctors = await db.doctors.find({}).to_list(length=None)
    patients = await db.patients.find({}).to_list(length=None)
    
    if not doctors or not patients:
        print("No doctors or patients found. Cannot create appointments.")
        return []
    
    appointments = []
    statuses = ["scheduled", "completed", "cancelled", "rescheduled"]
    reasons = [
        "Annual checkup", "Follow-up visit", "Consultation", "Routine examination",
        "Blood pressure check", "Preventive care", "Medication review", "Lab results"
    ]
    
    # Create appointments for the next 30 days
    for i in range(50):  # Create 50 sample appointments
        doctor = random.choice(doctors)
        patient = random.choice(patients)
        
        # Random appointment date within next 30 days
        days_ahead = random.randint(-5, 30)  # Some past appointments too
        appointment_date = datetime.now() + timedelta(days=days_ahead)
        
        # Set to business hours (9 AM - 5 PM)
        hour = random.choice([9, 10, 11, 14, 15, 16])  # Skip lunch hour (12-13)
        minute = random.choice([0, 30])
        appointment_date = appointment_date.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        
        # Adjust status based on date
        if appointment_date < datetime.now():
            status = random.choice(["completed", "cancelled"])
        else:
            status = random.choice(["scheduled", "rescheduled"])
        
        appointment = Appointment(
            patient_id=patient["patient_id"],
            patient_name=f"{patient['first_name']} {patient['last_name']}",
            patient_phone=patient.get("phone"),
            patient_email=patient.get("email"),
            doctor_name=f"Dr. {doctor['first_name']} {doctor['last_name']}",
            appointment_date=appointment_date,
            duration_minutes=random.choice([30, 45, 60]),
            status=status,
            reason=random.choice(reasons),
            notes=random.choice([
                None, "Patient reports feeling better", "Follow-up needed in 2 weeks",
                "Lab work ordered", "Prescription updated"
            ])
        )
        appointments.append(appointment.dict(by_alias=True))
    
    result = await db.appointments.insert_many(appointments)
    print(f"Created {len(result.inserted_ids)} appointments")
    return result.inserted_ids

async def create_sample_data():
    """Create all sample data"""
    print("Creating sample data for DocTalk AI...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        db = get_database()
        await db.doctors.delete_many({})
        await db.patients.delete_many({})
        await db.appointments.delete_many({})
        print("Cleared existing data")
        
        # Create sample data
        doctor_ids = await create_doctors()
        patient_ids = await create_patients()
        appointment_ids = await create_appointments()
        
        print("\n✅ Sample data created successfully!")
        print(f"   - {len(doctor_ids)} doctors")
        print(f"   - {len(patient_ids)} patients") 
        print(f"   - {len(appointment_ids)} appointments")
        
        return {
            "doctors": len(doctor_ids),
            "patients": len(patient_ids),
            "appointments": len(appointment_ids)
        }
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        raise e
    finally:
        # Close database connection
        await close_mongo_connection()
        print("Disconnected from MongoDB")

async def main():
    """Main function"""
    try:
        result = await create_sample_data()
        print(f"\n🎉 Sample data creation completed successfully!")
        return result
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())