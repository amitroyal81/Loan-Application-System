"""Database configuration and session management"""

import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.db.models import Base

logger = logging.getLogger(__name__)

# Connection URL
def get_database_url(async_driver=False):
    """Generate database connection URL"""
    from urllib.parse import quote
    driver = "aiomysql" if async_driver else "pymysql"
    # URL-encode password to handle special characters
    encoded_password = quote(settings.db_password, safe='')
    url = f"mysql+{driver}://{settings.db_user}:{encoded_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    return url


# Synchronous engine for table creation and synchronous operations
engine = None
AsyncSessionLocal = None


def init_db_engine():
    """Initialize database engine and session factory"""
    global engine, AsyncSessionLocal
    from urllib.parse import quote

    try:
        # Synchronous engine for setup and admin operations
        # URL-encode password to handle special characters
        encoded_password = quote(settings.db_password, safe='')
        db_url = f"mysql+pymysql://{settings.db_user}:{encoded_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

        engine = create_engine(
            db_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"charset": "utf8mb4"}
        )

        logger.info(f"Database engine initialized: {settings.db_host}:{settings.db_port}/{settings.db_name}")

    except Exception as e:
        logger.error(f"Failed to initialize database engine: {str(e)}")
        raise


def create_db_tables():
    """Create all database tables"""
    try:
        init_db_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def get_db_session():
    """Get synchronous database session"""
    if engine is None:
        init_db_engine()

    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


def close_db_connection():
    """Close database connection"""
    global engine
    if engine:
        engine.dispose()
        logger.info("Database connections closed")
