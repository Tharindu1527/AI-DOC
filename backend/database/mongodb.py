import motor.motor_asyncio
from config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    database: motor.motor_asyncio.AsyncIOMotorDatabase = None

# MongoDB instance
mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        # Create client with proper settings
        mongodb.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        
        # Use the database name from settings
        mongodb.database = mongodb.client[settings.database_name]
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.database_name}")
        
        # Create indexes for better performance
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = mongodb.database
        
        # Appointments collection indexes
        await db.appointments.create_index("appointment_date")
        await db.appointments.create_index("status")
        await db.appointments.create_index("patient_id")
        await db.appointments.create_index("doctor_name")
        await db.appointments.create_index([("patient_name", "text"), ("doctor_name", "text")])
        
        # Patients collection indexes
        await db.patients.create_index("patient_id", unique=True)
        await db.patients.create_index("phone")
        await db.patients.create_index("email")
        await db.patients.create_index([("first_name", "text"), ("last_name", "text"), ("email", "text")])
        
        # Doctors collection indexes
        await db.doctors.create_index("doctor_id", unique=True)
        await db.doctors.create_index("specialty")
        await db.doctors.create_index("is_available")
        await db.doctors.create_index("is_active")
        await db.doctors.create_index([("first_name", "text"), ("last_name", "text"), ("specialty", "text")])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        # Don't raise here as indexes are not critical for basic functionality

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Get database instance"""
    if mongodb.database is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return mongodb.database

async def health_check() -> bool:
    """Check if database is healthy"""
    try:
        await mongodb.client.admin.command('ping')
        return True
    except Exception:
        return False