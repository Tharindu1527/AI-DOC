import logging
import subprocess
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback
from datetime import datetime

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("doctalk.log") if not settings.debug else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up DocTalk AI backend...")
    try:
        from database.mongodb import connect_to_mongo
        await connect_to_mongo()
        logger.info("Database connection established")
        
        # Only validate API keys in production
        if not settings.debug:
            try:
                settings.validate_api_keys()
            except ValueError as e:
                logger.warning(f"API key validation failed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())
        # Don't raise - allow app to start without some features
    
    yield
    
    # Shutdown
    logger.info("Shutting down DocTalk AI backend...")
    try:
        from database.mongodb import close_mongo_connection
        await close_mongo_connection()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="DocTalk AI",
    description="Real-Time GP Booking Voice Agent API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper error handling
def safe_include_router(router_path: str, router_name: str, prefix: str = "/api"):
    """Safely include a router with error handling"""
    try:
        module = __import__(router_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix)
        logger.info(f"✅ {router_name} loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load {router_name}: {e}")
        return False

# Load all routers
safe_include_router("api.appointments", "router", "/api")
safe_include_router("api.voice", "router", "/api") 
safe_include_router("api.patients", "router", "/api")
safe_include_router("api.doctors", "router", "/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DocTalk AI - Real-Time GP Booking Voice Agent",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from database.mongodb import get_database, health_check as db_health
        db_status = "disconnected"
        try:
            if await db_health():
                db_status = "connected"
        except:
            pass
        
        # Test voice service
        voice_health = {"status": "unavailable"}
        try:
            from services.voice_service import voice_service
            voice_health = voice_service.health_check()
        except:
            pass
        
        return {
            "status": "healthy",
            "message": "DocTalk AI backend is running",
            "version": "1.0.0",
            "database": db_status,
            "services": voice_health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Admin endpoints for development
@app.post("/api/admin/create-sample-data")
async def create_sample_data():
    """Create sample data for testing"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    try:
        from create_sample_data import create_sample_data as create_data
        result = await create_data()
        return {"message": "Sample data created successfully", "result": result}
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create sample data: {str(e)}"}
        )

@app.post("/api/admin/clear-database")
async def clear_database():
    """Clear all database collections"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    try:
        from database.mongodb import get_database
        db = get_database()
        
        # Get all collection names
        collections = await db.list_collection_names()
        
        # Drop each collection
        for collection_name in collections:
            await db[collection_name].drop()
        
        return {"message": "Database cleared successfully", "collections_cleared": collections}
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error clearing database: {str(e)}"}
        )

@app.get("/api/admin/database-stats")
async def get_database_stats():
    """Get database statistics"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    try:
        from database.mongodb import get_database
        
        db = get_database()
        collections = await db.list_collection_names()
        
        stats = {}
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            stats[collection_name] = count
        
        return {
            "message": "Database statistics retrieved",
            "collections": stats,
            "total_collections": len(collections)
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting database stats: {str(e)}"}
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception on {request.url}: {exc}")
    logger.error(traceback.format_exc())
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "url": str(request.url),
                "traceback": traceback.format_exc()
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting DocTalk AI backend on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    
    # Check if required directories exist
    os.makedirs("logs", exist_ok=True)
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info" if not settings.debug else "debug",
            access_log=True,
            use_colors=True,
            reload_dirs=["./"] if settings.debug else None,
            # Connection management
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)