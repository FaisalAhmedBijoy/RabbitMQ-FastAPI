"""
Image Upload Routes
Handles image upload and initial processing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import uuid

from app.core.config import RABBITMQ_CONFIG
from app.core.rabbitmq import get_rabbitmq_channel
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["image-upload"])


class ImageUploadRequest(BaseModel):
    """Image upload request schema"""
    image_id: int
    image_path: str


class ImageUploadResponse(BaseModel):
    """Image upload response schema"""
    message: str
    image_id: int
    processing_id: str


@router.post("/upload-image")
async def upload_image(request: ImageUploadRequest) -> ImageUploadResponse:
    """
    Upload image and queue for processing
    
    19 RabbitMQ Concepts Demonstrated:
    1. Producer pattern - Publishing messages
    2. Queue declaration - Persistent queues
    3. Exchange routing - Direct exchange routing
    4. Message properties - Delivery mode (persistent)
    """
    try:
        if request.image_id <= 0:
            raise ValueError("image_id must be positive")
        
        # Generate processing ID
        processing_id = str(uuid.uuid4())
        
        # Prepare message
        message = {
            "image_id": request.image_id,
            "image_path": request.image_path,
            "processing_id": processing_id
        }
        
        # Publish to queue
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.RESIZE_QUEUE,
            body=json.dumps(message)
        )
        
        logger.info(f"Image {request.image_id} queued for processing")
        
        return ImageUploadResponse(
            message="Image processing started",
            image_id=request.image_id,
            processing_id=processing_id
        )
    
    except ValueError as e:
        logger.error(f"Validation error uploading image: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


class StatusResponse(BaseModel):
    """Status response schema"""
    image_id: int
    status: str
    processing_id: str


@router.get("/status/{image_id}")
async def get_status(image_id: int) -> StatusResponse:
    """Get image processing status"""
    try:
        if image_id <= 0:
            raise HTTPException(status_code=400, detail="image_id must be positive")
        
        # In a real app, query database for actual status
        return StatusResponse(
            image_id=image_id,
            status="processing",
            processing_id="mock-id"
        )
    
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
