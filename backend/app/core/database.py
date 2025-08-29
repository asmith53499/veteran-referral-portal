"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.config import settings
import structlog

logger = structlog.get_logger()

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=settings.debug   # SQL logging in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency to get database session
    Use this in FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database tables", error=str(e))
        raise

def check_db_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False
