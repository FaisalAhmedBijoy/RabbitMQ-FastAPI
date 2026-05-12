"""Image Upload Schemas"""

from pydantic import BaseModel
from typing import Optional


class ImageUploadRequest(BaseModel):
    """Image upload request"""
    image_id: int
    filename: str
    image_path: str
    image_size: int


class ImageUploadResponse(BaseModel):
    """Image upload response"""
    message: str
    status: str
    image_id: int
    timestamp: str


class ImageMetadata(BaseModel):
    """Image metadata"""
    image_id: int
    filename: str
    image_path: str
    image_size: int
    processing_id: Optional[str] = None
