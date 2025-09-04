import motor.motor_asyncio
from config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class MongoDB:
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    database: motor.motor_asyncio.AsyncIOMotorDatabase = None

# MongoDB instance
mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection with proper error handling and connection pooling"""
    try:
        # Create client with optimized settings for connection management
        mongodb.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            # Connection pool settings
            maxPoolSize=50,  # Maximum number of connections
            minPoolSize=10,  # Minimum number of connections
            maxIdleTimeMS=30000,  # Close connections after 30 seconds of inactivity
            
            # Timeout settings
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            
            # Health monitoring
            heartbeatFrequencyMS=10000,  # Check server health every 10 seconds
            
            # Connection cleanup
            waitQueueTimeoutMS=1000,  # Don't wait long for connections
            retryWrites=True,
            retryReads=True
        )
        
        # Use the database name from settings
        mongodb.database = mongodb.client[settings.database_name]
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.database_name}")
        
        # Create indexes for better performance
        await create_indexes()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = mongodb.database
        
        # Check if collections exist first
        collections = await db.list_collection_names()
        
        # Appointments collection indexes
        if 'appointments' in collections or True:  # Create even if collection doesn't exist
            try:
                # Create indexes with unique names to avoid conflicts
                await db.appointments.create_index("appointment_date", name="idx_appointment_date")
                await db.appointments.create_index("status", name="idx_status")
                await db.appointments.create_index("patient_id", name="idx_patient_id")
                await db.appointments.create_index("doctor_name", name="idx_doctor_name")
                await db.appointments.create_index([("patient_name", "text"), ("doctor_name", "text")], name="idx_search_text")
            except Exception as e:
                if "already exists" not in str(e):
                    logger.warning(f"Could not create appointments indexes: {e}")
        
        # Patients collection indexes
        if 'patients' in collections or True:
            try:
                await db.patients.create_index("patient_id", unique=True, name="idx_patient_id_unique")
                await db.patients.create_index("phone", name="idx_patient_phone")
                await db.patients.create_index("email", name="idx_patient_email")
                await db.patients.create_index([("first_name", "text"), ("last_name", "text"), ("email", "text")], name="idx_patient_search")
            except Exception as e:
                if "already exists" not in str(e):
                    logger.warning(f"Could not create patients indexes: {e}")
        
        # Doctors collection indexes
        if 'doctors' in collections or True:
            try:
                await db.doctors.create_index("doctor_id", unique=True, name="idx_doctor_id_unique")
                await db.doctors.create_index("specialty", name="idx_specialty")
                await db.doctors.create_index("is_available", name="idx_is_available")
                await db.doctors.create_index("is_active", name="idx_is_active")
                await db.doctors.create_index([("first_name", "text"), ("last_name", "text"), ("specialty", "text")], name="idx_doctor_search")
            except Exception as e:
                if "already exists" not in str(e):
                    logger.warning(f"Could not create doctors indexes: {e}")
        
        logger.info("Database indexes created/verified successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        # Don't raise here as indexes are not critical for basic functionality

async def close_mongo_connection():
    """Close database connection properly"""
    if mongodb.client:
        # Close all connections in the pool
        mongodb.client.close()
        
        # Wait for connections to close
        try:
            await asyncio.wait_for(
                mongodb.client.close(),
                timeout=5.0  # Wait max 5 seconds
            )
        except asyncio.TimeoutError:
            logger.warning("Database connection close timeout")
        except:
            pass  # Already closed
        
        mongodb.client = None
        mongodb.database = None
        logger.info("Disconnected from MongoDB")

def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Get database instance"""
    if mongodb.database is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return mongodb.database

async def health_check() -> bool:
    """Check if database is healthy"""
    try:
        if mongodb.client is None:
            return False
            
        # Use a shorter timeout for health checks
        await mongodb.client.admin.command('ping', maxTimeMS=2000)
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

async def ensure_connection():
    """Ensure database connection is active, reconnect if needed"""
    try:
        if not await health_check():
            logger.info("Database connection lost, attempting to reconnect...")
            await connect_to_mongo()
            return True
        return True
    except Exception as e:
        logger.error(f"Failed to ensure database connection: {e}")
        return False

# Connection retry decorator
def with_db_retry(max_retries: int = 3):
    """Decorator to retry database operations with reconnection"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # Ensure connection is healthy
                    if attempt > 0:  # Only check on retries
                        await ensure_connection()
                    
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
            
            # All retries failed
            logger.error(f"Database operation failed after {max_retries} attempts")
            raise last_exception
            
        return wrapper
    return decorator