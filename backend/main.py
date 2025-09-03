import logging
import subprocess
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from config import settings
from database.mongodb import connect_to_mongo, close_mongo_connection
from api.appointments import router as appointments_router
from api.voice import router as voice_router
from api.patients import router as patients_router
from api.doctors import router as doctors_router

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
        await connect_to_mongo()
        logger.info("Database connection established")
        
        # Validate API keys in production
        if not settings.debug:
            try:
                settings.validate_api_keys()
            except ValueError as e:
                logger.warning(f"API key validation failed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down DocTalk AI backend...")
    await close_mongo_connection()
    logger.info("Database connection closed")

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

# Include routers
app.include_router(appointments_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(doctors_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DocTalk AI - Real-Time GP Booking Voice Agent",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from database.mongodb import get_database
        from services.voice_service import voice_service
        
        # Test database connection
        db = get_database()
        await db.admin.command('ping')
        db_status = "connected"
        
        # Test voice service
        voice_health = voice_service.health_check()
        
        return {
            "status": "healthy",
            "message": "DocTalk AI backend is running",
            "version": "1.0.0",
            "database": db_status,
            "services": voice_health,
            "timestamp": str(datetime.now())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": str(e),
                "timestamp": str(datetime.now())
            }
        )

# Admin endpoints for development
@app.post("/api/admin/create-sample-data")
async def create_sample_data():
    """Create sample data for testing"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), "create_sample_data.py")
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True, 
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            return {"message": "Sample data created successfully", "output": result.stdout}
        else:
            logger.error(f"Sample data creation failed: {result.stderr}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to create sample data", "details": result.stderr}
            )
    except Exception as e:
        logger.error(f"Error running sample data script: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error running sample data script: {str(e)}"}
        )

@app.post("/api/admin/clear-database")
async def clear_database():
    """Clear all database collections"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), "db_utils.py")
        result = subprocess.run(
            [sys.executable, script_path, "clear"], 
            capture_output=True, 
            text=True, 
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            return {"message": "Database cleared successfully", "output": result.stdout}
        else:
            logger.error(f"Database clear failed: {result.stderr}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to clear database", "details": result.stderr}
            )
    except Exception as e:
        logger.error(f"Error running clear database script: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error running database clear script: {str(e)}"}
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
                "url": str(request.url)
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
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
            reload_dirs=["./"] if settings.debug else None
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)