"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, check_db_connection
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "veteran-referral-portal-api",
        "version": "1.0.0"
    }

@router.get("/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Test database connection
        if check_db_connection():
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Database connection successful"
            }
        else:
            raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        raise HTTPException(status_code=503, detail=f"Database health check failed: {str(e)}")

@router.get("/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    """Detailed health check with all system components"""
    health_status = {
        "status": "healthy",
        "service": "veteran-referral-portal-api",
        "version": "1.0.0",
        "components": {}
    }
    
    # Check database
    try:
        if check_db_connection():
            health_status["components"]["database"] = {
                "status": "healthy",
                "message": "Connected to PostgreSQL"
            }
        else:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "message": "Database connection failed"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Add more component checks here as needed
    
    return health_status
