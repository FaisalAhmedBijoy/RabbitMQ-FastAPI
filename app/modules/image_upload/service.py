"""Image Upload Service"""

import uuid
import json
from app.shared.base.worker import BaseService
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


class ImageUploadService(BaseService):
    """Service for handling image uploads"""
    
    def __init__(self):
        super().__init__("ImageUploadService")
    
    def execute(self, image_id: int, filename: str, image_path: str, image_size: int) -> dict:
        """Queue image for processing"""
        try:
            processing_id = str(uuid.uuid4())
            
            message = {
                "image_id": image_id,
                "filename": filename,
                "image_path": image_path,
                "image_size": image_size,
                "processing_id": processing_id
            }
            
            channel = get_rabbitmq_channel()
            channel.basic_publish(
                exchange="",
                routing_key=RABBITMQ_CONFIG.RESIZE_QUEUE,
                body=json.dumps(message)
            )
            
            self.logger.info(f"Image {image_id} queued for processing")
            return {"success": True, "processing_id": processing_id}
        
        except Exception as e:
            self.logger.error(f"Error queuing image: {str(e)}")
            return {"success": False, "error": str(e)}
