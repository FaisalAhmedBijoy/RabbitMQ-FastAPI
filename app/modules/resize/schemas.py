"""Resize Task Schemas"""

from pydantic import BaseModel


class ResizeTask(BaseModel):
    """Resize task"""
    image_id: int
    image_path: str
    processing_id: str
    target_width: int = 800
    target_height: int = 600


class ResizeResult(BaseModel):
    """Resize result"""
    image_id: int
    processing_id: str
    status: str
    output_path: str
