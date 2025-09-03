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
        mongodb.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
        mongodb.database = mongodb.client.doctalk
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.mongodb_url}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.database 