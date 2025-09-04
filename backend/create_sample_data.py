#!/usr/bin/env python3
"""
Quick sample data creator - run this to populate your database
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, time, date
import random

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def create_quick_sample_data():
    """Create minimal sample data quickly"""
    try:
        # Import here to avoid circular imports
        from database.mongodb import connect_to_mongo, close_mongo_connection, get_database
        
        print("🔌 Connecting to MongoDB...")
        await connect_to_mongo()
        db = get_database()
        
        print("🧹 Clearing existing data...")
        await db.doctors.delete_many({})
        await db.patients.delete_many({})
        await db.appointments.delete_many({})
        
        print("👨‍⚕️ Creating doctors...")
        doctors_data = [
            {
                "doctor_id": f"D{datetime.now().strftime('%Y%m%d')}0001",
                "first_name": "John", "last_name": "Smith", "title": "Dr.",
                "specialty": "General Practice", "department": "Family Medicine",
                "years_experience": 15, "email": "j.smith@hospital.com", "phone": "+1-555-0101",
                "is_available": True, "is_active": True, "rating": 4.5, "total_reviews": 120,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
            },
            {
                "doctor_id": f"D{datetime.now().strftime('%Y%m%d')}0002",
                "first_name": "Sarah", "last_name": "Johnson", "title": "Dr.",
                "specialty": "Cardiology", "department": "Cardiology",
                "years_experience": 12, "email": "s.johnson@hospital.com", "phone": "+1-555-0102",
                "is_available": True, "is_active": True, "rating": 4.8, "total_reviews": 200,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
            },
            {
                "doctor_id": f"D{datetime.now().strftime('%Y%m%d')}0003",
                "first_name": "Michael", "last_name": "Williams", "title": "Dr.",
                "specialty": "Pediatrics", "department": "Pediatrics",
                "years_experience": 8, "email": "m.williams@hospital.com", "phone": "+1-555-0103",
                "is_available": True, "is_active": True, "rating": 4.7, "total_reviews": 150,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
            }
        ]
        
        result = await db.doctors.insert_many(doctors_data)
        print(f"   ✅ Created {len(result.inserted_ids)} doctors")
        
        print("👥 Creating patients...")
        patients_data = [
            {
                "patient_id": f"P{datetime.now().strftime('%Y%m%d')}0001",
                "first_name": "Alice", "last_name": "Cooper",
                "email": "alice.cooper@email.com", "phone": "+1-555-1001",
                "gender": "female", "city": "New York", "state": "NY",
                "date_of_birth": date(1985, 5, 15), "is_active": True,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
            },
            {
                "patient_id": f"P{datetime.now().strftime('%Y%m%d')}0002",
                "first_name": "Bob", "last_name": "Anderson",
                "email": "bob.anderson@email.com", "phone": "+1-555-1002",
                "gender": "male", "city": "Los Angeles", "state": "CA",
                "date_of_birth": date(1978, 8, 22), "is_active": True,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
            },
            {
                "patient_id": f"P{datetime.now().strftime('%Y%m%d')}0003",
                "first_name": "Carol", "last_name": "Thomas",
                "email": "carol.thomas@email.com", "phone": "+1-555-1003",
                "gender": "female", "city": "Chicago", "state": "IL",
                "date_of_birth": date(1992, 12, 3), "is_active": True,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
            }
        ]
        
        result = await db.patients.insert_many(patients_data)
        print(f"   ✅ Created {len(result.inserted_ids)} patients")
        
        print("📅 Creating appointments...")
        appointments_data = [
            {
                "patient_id": patients_data[0]["patient_id"],
                "patient_name": "Alice Cooper",
                "patient_phone": "+1-555-1001",
                "doctor_name": "Dr. John Smith",
                "appointment_date": datetime.now() + timedelta(days=1, hours=10),
                "duration_minutes": 30,
                "status": "scheduled",
                "reason": "Annual checkup",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "patient_id": patients_data[1]["patient_id"],
                "patient_name": "Bob Anderson",
                "patient_phone": "+1-555-1002",
                "doctor_name": "Dr. Sarah Johnson",
                "appointment_date": datetime.now() + timedelta(hours=2),
                "duration_minutes": 45,
                "status": "scheduled",
                "reason": "Cardiology consultation",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "patient_id": patients_data[2]["patient_id"],
                "patient_name": "Carol Thomas",
                "patient_phone": "+1-555-1003",
                "doctor_name": "Dr. Michael Williams",
                "appointment_date": datetime.now() - timedelta(days=1),
                "duration_minutes": 30,
                "status": "completed",
                "reason": "Pediatric check",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await db.appointments.insert_many(appointments_data)
        print(f"   ✅ Created {len(result.inserted_ids)} appointments")
        
        print("\n🎉 Sample data created successfully!")
        print(f"   - {len(doctors_data)} doctors")
        print(f"   - {len(patients_data)} patients")
        print(f"   - {len(appointments_data)} appointments")
        
        await close_mongo_connection()
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(create_quick_sample_data())