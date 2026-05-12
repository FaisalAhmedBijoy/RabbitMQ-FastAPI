"""
Thumbnail Worker - Handles thumbnail generation
"""

import time
import random
from typing import Dict, Any

from app.core.config import RABBITMQ_CONFIG, APP_CONFIG
from app.shared.helpers.logger import setup_logger
from app.workers.base import BaseWorker

logger = setup_logger(__name__)


class ThumbnailWorker(BaseWorker):
    """Worker for generating thumbnails"""
    
    def __init__(self, worker_id: int = 1):
        super().__init__(RABBITMQ_CONFIG.THUMBNAIL_QUEUE, f"ThumbnailWorker-{worker_id}")
        self.worker_id = worker_id
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate thumbnail generation
        
        Args:
            message: Image metadata message
        
        Returns:
            Processing result
        """
        image_id = message.get('image_id')
        filename = message.get('filename')
        
        logger.info(f"{self.worker_name}: Processing thumbnail for image {image_id} ({filename})")
        
        # Simulate random failure for demonstration
        if random.randint(1, 8) == 3:
            raise Exception(f"Simulated thumbnail generation failure for {filename}")
        
        # Simulate processing with delay
        logger.info(f"{self.worker_name}: Generating thumbnail for {filename}... (simulated)")
        time.sleep(3)  # Simulate processing time
        
        result = {
            'image_id': image_id,
            'task_type': 'thumbnail',
            'status': 'completed',
            'details': {
                'thumbnail_size': '150x150',
                'quality': '90',
                'format': 'JPEG',
                'processing_time': '3.1s',
                'worker_id': self.worker_id,
                'thumbnail_path': f'/thumbnails/{filename}'
            }
        }
        
        logger.info(f"{self.worker_name}: Thumbnail generated for image {image_id}")
        return result


if __name__ == "__main__":
    worker = ThumbnailWorker()
    worker.start_consuming()
