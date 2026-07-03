"""FastAPI main application entry point"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from src.config import settings
from src.db.database import create_db_tables, close_db_connection

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Loan Approval System",
    description="Multi-agent AI system for intelligent loan approval decisions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Agentic AI Loan Approval System starting up")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database
    try:
        logger.info(f"Initializing database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        create_db_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {str(e)}. System will use in-memory storage.")
        logger.info("To use MySQL, ensure the database server is running and credentials are correct.")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Agentic AI Loan Approval System shutting down")

    # Close database connections
    try:
        close_db_connection()
    except Exception as e:
        logger.warning(f"Error closing database connection: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agentic AI Loan Approval System",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
