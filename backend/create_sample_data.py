"""
Sample data creation script for DocTalk AI
Run this to populate the database with sample doctors, patients, and appointments
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import connect_to_mongo, close_mongo_connection
from services.doctor_service import doctor_service
from services.patient_service import patient_service
from services.appointment_service import appointment_service
from models.doctor import DoctorCreate, WorkingHours
from models.patient import PatientCreate
from models.appointment import AppointmentCreate
from datetime import time

async def create_sample_doctors():
    """Create sample doctors"""
    print("Creating sample doctors...")
    
    # Default working hours (9 AM to 5 PM, Monday to Friday)
    default_hours = [
        WorkingHours(day="Monday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Tuesday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Wednesday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Thursday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Friday", start_time=time(9, 0), end_time=time(17, 0), is_available=True),
        WorkingHours(day="Saturday", start_time=time(9, 0), end_time=time(13, 0), is_available=False),
        WorkingHours(day="Sunday", start_time=time(9, 0), end_time=time(13, 0), is_available=False)
    ]
    
    sample_doctors = [
        DoctorCreate(
            first_name="John",
            last_name="Smith",
            specialty="General Practice",
            department="Primary Care",
            email="j.smith@doctalk.com",
            phone="(555) 123-4567",
            office_location="Room 101",
            education=["MD from Harvard Medical School", "Residency at Mayo Clinic"],
            certifications=["Board Certified in Family Medicine", "ACLS Certified"],
            years_experience=15,
            languages=["English", "Spanish"],
            bio="Dr. Smith is a dedicated family physician with over 15 years of experience providing comprehensive primary care.",
            consultation_fee=150.0,
            working_hours=default_hours,
            rating=4.8,
            total_reviews=127
        ),
        DoctorCreate(
            first_name="Emily",
            last_name="Johnson",
            specialty="Cardiology",
            department="Cardiology",
            email="e.johnson@doctalk.com",
            phone="(555) 234-5678",
            office_location="Room 205",
            education=["MD from Johns Hopkins", "Cardiology Fellowship at Cleveland Clinic"],
            certifications=["Board Certified in Cardiology", "Interventional Cardiology"],
            years_experience=12,
            languages=["English"],
            bio="Dr. Johnson specializes in interventional cardiology with expertise in complex cardiac procedures.",
            consultation_fee=250.0,
            working_hours=default_hours,
            rating=4.9,
            total_reviews=89
        ),
        DoctorCreate(
            first_name="Michael",
            last_name="Williams",
            specialty="Pediatrics",
            department="Pediatrics",
            email="m.williams@doctalk.com",
            phone="(555) 345-6789",
            office_location="Room 150",
            education=["MD from University of Pennsylvania", "Pediatric Residency at CHOP"],
            certifications=["Board Certified in Pediatrics", "PALS Certified"],
            years_experience=8,
            languages=["English", "French"],
            bio="Dr. Williams is passionate about pediatric care and has extensive experience with childhood development.",
            consultation_fee=120.0,
            working_hours=default_hours,
            rating=4.7,
            total_reviews=156
        ),
        DoctorCreate(
            first_name="Sarah",
            last_name="Brown",
            specialty="Dermatology",
            department="Dermatology",
            email="s.brown@doctalk.com",
            phone="(555) 456-7890",
            office_location="Room 301",
            education=["MD from Stanford University", "Dermatology Residency at UCSF"],
            certifications=["Board Certified in Dermatology", "Mohs Surgery Certified"],
            years_experience=10,
            languages=["English", "German"],
            bio="Dr. Brown specializes in medical and surgical dermatology with a focus on skin cancer treatment.",
            consultation_fee=200.0,
            working_hours=default_hours,
            rating=4.8,
            total_reviews=94
        ),
        DoctorCreate(
            first_name="David",
            last_name="Davis",
            specialty="Orthopedics",
            department="Orthopedic Surgery",
            email="d.davis@doctalk.com",
            phone="(555) 567-8901",
            office_location="Room 401",
            education=["MD from Yale University", "Orthopedic Surgery Residency at Hospital for Special Surgery"],
            certifications=["Board Certified in Orthopedic Surgery", "Sports Medicine Certified"],
            years_experience=18,
            languages=["English"],
            bio="Dr. Davis is an experienced orthopedic surgeon specializing in sports medicine and joint replacement.",
            consultation_fee=300.0,
            working_hours=default_hours,
            rating=4.9,
            total_reviews=76
        ),
        DoctorCreate(
            first_name="Lisa",
            last_name="Miller",
            specialty="Neurology",
            department="Neurology",
            email="l.miller@doctalk.com",
            phone="(555) 678-9012",
            office_location="Room 501",
            education=["MD from Duke University", "Neurology Residency at Mass General"],
            certifications=["Board Certified in Neurology", "Epilepsy Specialist"],
            years_experience=14,
            languages=["English", "Italian"],
            bio="Dr. Miller is a neurologist with expertise in epilepsy treatment and neurological disorders.",
            consultation_fee=275.0,
            working_hours=default_hours,
            rating=4.6,
            total_reviews=103
        ),
        DoctorCreate(
            first_name="Robert",
            last_name="Wilson",
            specialty="Psychiatry",
            department="Mental Health",
            email="r.wilson@doctalk.com",
            phone="(555) 789-0123",
            office_location="Room 601",
            education=["MD from Columbia University", "Psychiatry Residency at Bellevue"],
            certifications=["Board Certified in Psychiatry", "Addiction Medicine Certified"],
            years_experience=16,
            languages=["English", "Portuguese"],
            bio="Dr. Wilson is a psychiatrist specializing in mood disorders and addiction treatment.",
            consultation_fee=180.0,
            working_hours=default_hours,
            rating=4.7,
            total_reviews=134
        ),
        DoctorCreate(
            first_name="Jennifer",
            last_name="Moore",
            specialty="Endocrinology",
            department="Endocrinology",
            email="j.moore@doctalk.com",
            phone="(555) 890-1234",
            office_location="Room 701",
            education=["MD from Northwestern University", "Endocrinology Fellowship at Mayo Clinic"],
            certifications=["Board Certified in Endocrinology", "Diabetes Educator"],
            years_experience=11,
            languages=["English", "Mandarin"],
            bio="Dr. Moore specializes in diabetes management and hormonal disorders.",
            consultation_fee=220.0,
            working_hours=default_hours,
            rating=4.8,
            total_reviews=87
        )
    ]
    
    created_doctors = []
    for doctor_data in sample_doctors:
        try:
            doctor = await doctor_service.create_doctor(doctor_data)
            created_doctors.append(doctor)
            print(f"Created doctor: {doctor.title} {doctor.first_name} {doctor.last_name} - {doctor.specialty}")
        except Exception as e:
            print(f"Error creating doctor: {e}")
    
    return created_doctors

async def create_sample_patients():
    """Create sample patients"""
    print("Creating sample patients...")
    
    sample_patients = [
        PatientCreate(
            first_name="Alice",
            last_name="Anderson",
            email="alice.anderson@email.com",
            phone="(555) 111-2222",
            date_of_birth=datetime(1985, 3, 15),
            gender="female",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
            emergency_contact_name="Bob Anderson",
            emergency_contact_phone="(555) 111-3333",
            medical_history=["Hypertension", "Diabetes Type 2"],
            allergies=["Penicillin", "Peanuts"],
            medications=["Metformin", "Lisinopril"],
            insurance_provider="Blue Cross Blue Shield",
            insurance_id="BC123456789"
        ),
        PatientCreate(
            first_name="Bob",
            last_name="Baker",
            email="bob.baker@email.com",
            phone="(555) 222-3333",
            date_of_birth=datetime(1978, 7, 22),
            gender="male",
            address="456 Oak Ave",
            city="Springfield",
            state="IL",
            zip_code="62702",
            emergency_contact_name="Carol Baker",
            emergency_contact_phone="(555) 222-4444",
            medical_history=["High Cholesterol"],
            allergies=["Shellfish"],
            medications=["Atorvastatin"],
            insurance_provider="Aetna",
            insurance_id="AET987654321"
        ),
        PatientCreate(
            first_name="Carol",
            last_name="Chen",
            email="carol.chen@email.com",
            phone="(555) 333-4444",
            date_of_birth=datetime(1992, 11, 8),
            gender="female",
            address="789 Pine St",
            city="Springfield",
            state="IL",
            zip_code="62703",
            emergency_contact_name="David Chen",
            emergency_contact_phone="(555) 333-5555",
            medical_history=["Asthma"],
            allergies=["Dust mites", "Pet dander"],
            medications=["Albuterol inhaler"],
            insurance_provider="Cigna",
            insurance_id="CIG456789123"
        ),
        PatientCreate(
            first_name="David",
            last_name="Davis",
            email="david.davis@email.com",
            phone="(555) 444-5555",
            date_of_birth=datetime(1965, 5, 30),
            gender="male",
            address="321 Elm St",
            city="Springfield",
            state="IL",
            zip_code="62704",
            emergency_contact_name="Emma Davis",
            emergency_contact_phone="(555) 444-6666",
            medical_history=["Arthritis", "High Blood Pressure"],
            allergies=["NSAIDs"],
            medications=["Ibuprofen", "Amlodipine"],
            insurance_provider="UnitedHealth",
            insurance_id="UH789123456"
        ),
        PatientCreate(
            first_name="Emma",
            last_name="Evans",
            email="emma.evans@email.com",
            phone="(555) 555-6666",
            date_of_birth=datetime(1990, 9, 12),
            gender="female",
            address="654 Birch Rd",
            city="Springfield",
            state="IL",
            zip_code="62705",
            emergency_contact_name="Frank Evans",
            emergency_contact_phone="(555) 555-7777",
            medical_history=["Migraine"],
            allergies=["Latex"],
            medications=["Sumatriptan"],
            insurance_provider="Humana",
            insurance_id="HUM123789456"
        ),
        PatientCreate(
            first_name="Frank",
            last_name="Fisher",
            email="frank.fisher@email.com",
            phone="(555) 666-7777",
            date_of_birth=datetime(1970, 12, 3),
            gender="male",
            address="987 Cedar Ln",
            city="Springfield",
            state="IL",
            zip_code="62706",
            emergency_contact_name="Grace Fisher",
            emergency_contact_phone="(555) 666-8888",
            medical_history=["COPD"],
            allergies=["Sulfa drugs"],
            medications=["Spiriva", "Albuterol"],
            insurance_provider="Kaiser Permanente",
            insurance_id="KP456123789"
        ),
        PatientCreate(
            first_name="Grace",
            last_name="Garcia",
            email="grace.garcia@email.com",
            phone="(555) 777-8888",
            date_of_birth=datetime(1988, 2, 18),
            gender="female",
            address="147 Maple Ave",
            city="Springfield",
            state="IL",
            zip_code="62707",
            emergency_contact_name="Henry Garcia",
            emergency_contact_phone="(555) 777-9999",
            medical_history=["Anxiety", "Depression"],
            allergies=["Codeine"],
            medications=["Sertraline", "Lorazepam"],
            insurance_provider="Anthem",
            insurance_id="ANT789456123"
        ),
        PatientCreate(
            first_name="Henry",
            last_name="Harris",
            email="henry.harris@email.com",
            phone="(555) 888-9999",
            date_of_birth=datetime(1995, 6, 25),
            gender="male",
            address="258 Willow St",
            city="Springfield",
            state="IL",
            zip_code="62708",
            emergency_contact_name="Ivy Harris",
            emergency_contact_phone="(555) 888-0000",
            medical_history=["Allergic Rhinitis"],
            allergies=["Pollen", "Mold"],
            medications=["Claritin"],
            insurance_provider="Blue Cross Blue Shield",
            insurance_id="BC987123456"
        ),
        PatientCreate(
            first_name="Ivy",
            last_name="Jackson",
            email="ivy.jackson@email.com",
            phone="(555) 999-0000",
            date_of_birth=datetime(1982, 10, 7),
            gender="female",
            address="369 Spruce Dr",
            city="Springfield",
            state="IL",
            zip_code="62709",
            emergency_contact_name="Jack Jackson",
            emergency_contact_phone="(555) 999-1111",
            medical_history=["Thyroid disorder"],
            allergies=["Iodine"],
            medications=["Levothyroxine"],
            insurance_provider="Medicaid",
            insurance_id="MCD123456789"
        ),
        PatientCreate(
            first_name="Jack",
            last_name="Johnson",
            email="jack.johnson@email.com",
            phone="(555) 000-1111",
            date_of_birth=datetime(2005, 4, 14),
            gender="male",
            address="741 Poplar St",
            city="Springfield",
            state="IL",
            zip_code="62710",
            emergency_contact_name="Kate Johnson",
            emergency_contact_phone="(555) 000-2222",
            medical_history=["ADHD"],
            allergies=["Food coloring"],
            medications=["Adderall"],
            insurance_provider="CHIP",
            insurance_id="CHIP456789123"
        )
    ]
    
    created_patients = []
    for patient_data in sample_patients:
        try:
            patient = await patient_service.create_patient(patient_data)
            created_patients.append(patient)
            print(f"Created patient: {patient.first_name} {patient.last_name} (ID: {patient.patient_id})")
        except Exception as e:
            print(f"Error creating patient: {e}")
    
    return created_patients

async def create_sample_appointments(doctors: List, patients: List):
    """Create sample appointments"""
    print("Creating sample appointments...")
    
    # Create appointments for the next few days
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    sample_appointments = []
    
    # Today's appointments
    for i in range(5):
        appointment_time = base_date + timedelta(hours=i*2)
        sample_appointments.append(
            AppointmentCreate(
                patient_id=patients[i % len(patients)].patient_id,
                patient_name=f"{patients[i % len(patients)].first_name} {patients[i % len(patients)].last_name}",
                patient_phone=patients[i % len(patients)].phone,
                doctor_name=f"Dr. {doctors[i % len(doctors)].last_name}",
                appointment_date=appointment_time,
                duration_minutes=30,
                status="scheduled",
                notes=f"Regular checkup for {patients[i % len(patients)].first_name}"
            )
        )
    
    # Tomorrow's appointments
    tomorrow = base_date + timedelta(days=1)
    for i in range(6):
        appointment_time = tomorrow + timedelta(hours=i*1.5)
        sample_appointments.append(
            AppointmentCreate(
                patient_id=patients[(i+1) % len(patients)].patient_id,
                patient_name=f"{patients[(i+1) % len(patients)].first_name} {patients[(i+1) % len(patients)].last_name}",
                patient_phone=patients[(i+1) % len(patients)].phone,
                doctor_name=f"Dr. {doctors[(i+1) % len(doctors)].last_name}",
                appointment_date=appointment_time,
                duration_minutes=45,
                status="scheduled",
                notes=f"Follow-up appointment for {patients[(i+1) % len(patients)].first_name}"
            )
        )
    
    # Past appointments (completed)
    yesterday = base_date - timedelta(days=1)
    for i in range(4):
        appointment_time = yesterday + timedelta(hours=i*2)
        sample_appointments.append(
            AppointmentCreate(
                patient_id=patients[(i+2) % len(patients)].patient_id,
                patient_name=f"{patients[(i+2) % len(patients)].first_name} {patients[(i+2) % len(patients)].last_name}",
                patient_phone=patients[(i+2) % len(patients)].phone,
                doctor_name=f"Dr. {doctors[(i+2) % len(doctors)].last_name}",
                appointment_date=appointment_time,
                duration_minutes=30,
                status="completed",
                notes=f"Annual physical for {patients[(i+2) % len(patients)].first_name}"
            )
        )
    
    # Some cancelled appointments
    for i in range(2):
        appointment_time = base_date + timedelta(days=2, hours=i*3)
        sample_appointments.append(
            AppointmentCreate(
                patient_id=patients[(i+3) % len(patients)].patient_id,
                patient_name=f"{patients[(i+3) % len(patients)].first_name} {patients[(i+3) % len(patients)].last_name}",
                patient_phone=patients[(i+3) % len(patients)].phone,
                doctor_name=f"Dr. {doctors[(i+3) % len(doctors)].last_name}",
                appointment_date=appointment_time,
                duration_minutes=30,
                status="cancelled",
                notes=f"Cancelled by patient"
            )
        )
    
    created_appointments = []
    for appointment_data in sample_appointments:
        try:
            appointment = await appointment_service.create_appointment(appointment_data)
            created_appointments.append(appointment)
            print(f"Created appointment: {appointment.patient_name} with {appointment.doctor_name} on {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')} - {appointment.status}")
        except Exception as e:
            print(f"Error creating appointment: {e}")
    
    return created_appointments

async def main():
    """Main function to create all sample data"""
    print("Starting sample data creation for DocTalk AI...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB")
        
        # Create sample data
        doctors = await create_sample_doctors()
        patients = await create_sample_patients()
        appointments = await create_sample_appointments(doctors, patients)
        
        print(f"\nSample data creation completed!")
        print(f"Created {len(doctors)} doctors")
        print(f"Created {len(patients)} patients") 
        print(f"Created {len(appointments)} appointments")
        
    except Exception as e:
        print(f"Error during sample data creation: {e}")
    finally:
        # Close database connection
        await close_mongo_connection()
        print("Disconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(main())
