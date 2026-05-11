"""
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from app.config import APP_CONFIG
from app.utils.logger import setup_logger
from app.rabbitmq import get_rabbitmq_connection
from app.queues import setup_rabbitmq
from app.producers import publish_image_task
from app.schemas.image import ImageUploadRequest, ImageUploadResponse

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=APP_CONFIG.APP_NAME,
    description="Async Image Processing Pipeline with RabbitMQ",
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


@app.on_event("startup")
async def startup_event():
    """Initialize RabbitMQ on startup"""
    try:
        logger.info("Starting up Async Image Processing Pipeline...")
        rabbitmq_conn = get_rabbitmq_connection()
        rabbitmq_conn.connect()
        setup_rabbitmq()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Shutting down application...")
        rabbitmq_conn = get_rabbitmq_connection()
        rabbitmq_conn.disconnect()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Async Image Processing Pipeline",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/upload-image", response_model=ImageUploadResponse, tags=["Image Processing"])
async def upload_image(request: ImageUploadRequest):
    """
    Upload image metadata and queue for processing
    
    The API immediately returns while RabbitMQ handles processing asynchronously.
    
    Request body:
    - image_id: Unique image identifier
    - filename: Original filename
    - image_path: Path to image file
    - image_size: Image size
    
    Returns:
    - message: Confirmation message
    - status: Current status (queued)
    - image_id: The image ID
    - timestamp: Request timestamp
    """
    try:
        # Validate image ID
        if request.image_id <= 0:
            raise HTTPException(status_code=400, detail="image_id must be positive")
        
        # Create uploads directory if it doesn't exist
        os.makedirs(APP_CONFIG.UPLOAD_DIR, exist_ok=True)
        
        # Publish to RabbitMQ
        success = publish_image_task(
            image_id=request.image_id,
            filename=request.filename,
            image_path=request.image_path,
            image_size=request.image_size
        )
        
        if not success:
            logger.error(f"Failed to publish image {request.image_id} to RabbitMQ")
            raise HTTPException(
                status_code=500,
                detail="Failed to queue image for processing"
            )
        
        logger.info(f"Image {request.image_id} queued for processing")
        
        return ImageUploadResponse(
            message="Image processing started",
            status="queued",
            image_id=request.image_id,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/status/{image_id}", tags=["Image Processing"])
async def get_image_status(image_id: int):
    """
    Get processing status of an image
    
    Note: In a production system, this would query a database.
    For this demo, we return placeholder data.
    """
    return {
        "image_id": image_id,
        "status": "processing",
        "tasks": {
            "resize": "completed",
            "thumbnail": "in_progress",
            "ocr": "pending",
            "ai_tagging": "pending"
        },
        "timestamp": datetime.now().isoformat()
    }
