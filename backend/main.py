import logging
import subprocess
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
from database.mongodb import connect_to_mongo, close_mongo_connection
from api.appointments import router as appointments_router
from api.voice import router as voice_router
from api.patients import router as patients_router
from api.doctors import router as doctors_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up DocTalk AI backend...")
    try:
        await connect_to_mongo()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
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
    lifespan=lifespan
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
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "DocTalk AI backend is running",
        "version": "1.0.0"
    }

# Admin endpoints for development
@app.post("/api/admin/create-sample-data")
async def create_sample_data():
    """Create sample data for testing"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "create_sample_data.py")
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            return {"message": "Sample data created successfully", "output": result.stdout}
        else:
            return {"error": "Failed to create sample data", "output": result.stderr}
    except Exception as e:
        return {"error": f"Error running sample data script: {str(e)}"}

@app.post("/api/admin/clear-database")
async def clear_database():
    """Clear all database collections"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "db_utils.py")
        result = subprocess.run([sys.executable, script_path, "clear"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            return {"message": "Database cleared successfully", "output": result.stdout}
        else:
            return {"error": "Failed to clear database", "output": result.stderr}
    except Exception as e:
        return {"error": f"Error running clear database script: {str(e)}"}

@app.get("/api/admin/database-stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "db_utils.py")
        result = subprocess.run([sys.executable, script_path, "stats"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            return {"message": "Database stats retrieved", "output": result.stdout}
        else:
            return {"error": "Failed to get database stats", "output": result.stderr}
    except Exception as e:
        return {"error": f"Error running database stats script: {str(e)}"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting DocTalk AI backend on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    ) 