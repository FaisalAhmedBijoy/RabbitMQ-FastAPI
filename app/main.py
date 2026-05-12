"""
Main FastAPI Application
Entry point for the Async Image Processing Pipeline
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import APP_CONFIG
from app.shared.helpers.logger import setup_logger
from app.routes import image_upload_routes, monitoring_routes

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    logger.info("Starting Async Image Processing Pipeline...")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=APP_CONFIG.APP_NAME,
    description="Async image processing with RabbitMQ",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitoring_routes.router)
app.include_router(image_upload_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=APP_CONFIG.API_HOST,
        port=APP_CONFIG.API_PORT,
        log_level=APP_CONFIG.LOG_LEVEL.lower()
    )
