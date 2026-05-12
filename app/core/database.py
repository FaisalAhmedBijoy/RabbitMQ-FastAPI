"""
Database Configuration and Session Management
Handles database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import DATABASE_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)

# Create database engine
engine = create_engine(
    DATABASE_CONFIG.DATABASE_URL,
    echo=DATABASE_CONFIG.ECHO,
    connect_args={"check_same_thread": False}  # For SQLite only
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Get database session for dependency injection
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        logger.info("Initializing database...")
        # Import models here to avoid circular imports
        # from app.modules.image_upload.model import Base
        # Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
