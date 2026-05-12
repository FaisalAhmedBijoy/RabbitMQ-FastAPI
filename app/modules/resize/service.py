"""Resize Service"""

import time
import random
from app.shared.base.worker import BaseService
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


class ResizeService(BaseService):
    """Service for resizing images"""
    
    FAILURE_RATE = 10  # 1 in 10 chance of failure
    
    def __init__(self):
        super().__init__("ResizeService")
    
    def execute(self, message: dict) -> dict:
        """Process resize task"""
        try:
            image_id = message.get("image_id")
            processing_id = message.get("processing_id")
            
            self.logger.info(f"Resizing image {image_id}")
            
            # Simulate processing delay
            time.sleep(5)
            
            # Simulate occasional failures
            if random.randint(1, self.FAILURE_RATE) == 1:
                raise Exception(f"Simulated resize failure for image {image_id}")
            
            return {
                "image_id": image_id,
                "processing_id": processing_id,
                "status": "completed",
                "output_path": f"app/uploads/resized/{image_id}_resized.jpg"
            }
        
        except Exception as e:
            self.logger.error(f"Error resizing image: {str(e)}")
            raise
