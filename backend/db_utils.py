"""
Database management utilities for DocTalk AI
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import connect_to_mongo, close_mongo_connection, db

async def clear_database():
    """Clear all collections in the database"""
    print("Clearing all database collections...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB")
        
        # Get all collection names
        collections = await db.list_collection_names()
        print(f"Found collections: {collections}")
        
        # Drop each collection
        for collection_name in collections:
            await db[collection_name].drop()
            print(f"Dropped collection: {collection_name}")
        
        print("Database cleared successfully!")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
    finally:
        # Close database connection
        await close_mongo_connection()
        print("Disconnected from MongoDB")

async def get_database_stats():
    """Get statistics about the database"""
    print("Getting database statistics...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("Connected to MongoDB")
        
        # Get collection stats
        collections = await db.list_collection_names()
        
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            print(f"{collection_name}: {count} documents")
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
    finally:
        # Close database connection
        await close_mongo_connection()
        print("Disconnected from MongoDB")

async def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_utils.py <command>")
        print("Commands: clear, stats")
        return
    
    command = sys.argv[1].lower()
    
    if command == "clear":
        await clear_database()
    elif command == "stats":
        await get_database_stats()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: clear, stats")

if __name__ == "__main__":
    asyncio.run(main())
