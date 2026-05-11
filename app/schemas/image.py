"""
Request and Response schemas for the API
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImageUploadRequest(BaseModel):
    """Image upload request schema"""
    image_id: int
    filename: str
    image_path: str
    image_size: str
    upload_time: Optional[str] = None

    class Config:
        example = {
            "image_id": 1,
            "filename": "car.jpg",
            "image_path": "/uploads/car.jpg",
            "image_size": "5MB"
        }


class ImageUploadResponse(BaseModel):
    """Image upload response schema"""
    message: str
    status: str
    image_id: int
    timestamp: str

    class Config:
        example = {
            "message": "Image processing started",
            "status": "queued",
            "image_id": 1,
            "timestamp": "2024-01-15T10:30:00"
        }


class ProcessingMessage(BaseModel):
    """Message structure for RabbitMQ"""
    image_id: int
    filename: str
    image_path: str
    image_size: str
    retry_count: int = 0
    timestamp: str


class ProcessingResult(BaseModel):
    """Result of processing"""
    image_id: int
    task_type: str
    status: str
    result: dict
    timestamp: str


class ResizeResult(ProcessingResult):
    """Resize task result"""
    pass


class ThumbnailResult(ProcessingResult):
    """Thumbnail task result"""
    pass


class OCRResult(ProcessingResult):
    """OCR task result"""
    pass


class AITaggingResult(ProcessingResult):
    """AI Tagging task result"""
    pass
