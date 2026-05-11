"""
Resize Worker - Handles image resizing and optimization
"""

import time
import random
from typing import Dict, Any

from app.config import RABBITMQ_CONFIG, APP_CONFIG
from app.utils.logger import setup_logger
from app.workers.base import BaseWorker

logger = setup_logger(__name__)


class ResizeWorker(BaseWorker):
    """Worker for resizing and optimizing images"""
    
    def __init__(self, worker_id: int = 1):
        super().__init__(RABBITMQ_CONFIG.RESIZE_QUEUE, f"ResizeWorker-{worker_id}")
        self.worker_id = worker_id
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate image resizing
        
        Args:
            message: Image metadata message
        
        Returns:
            Processing result
        """
        image_id = message.get('image_id')
        filename = message.get('filename')
        
        logger.info(f"{self.worker_name}: Processing resize for image {image_id} ({filename})")
        
        # Simulate random failure for demonstration
        if random.randint(1, 10) == 5:
            raise Exception(f"Simulated resize failure for {filename}")
        
        # Simulate heavy processing with delay
        logger.info(f"{self.worker_name}: Resizing image {filename}... (simulated)")
        time.sleep(5)  # Simulate processing time
        
        result = {
            'image_id': image_id,
            'task_type': 'resize',
            'status': 'completed',
            'details': {
                'original_size': message.get('image_size'),
                'resized_dimensions': '800x600',
                'compression_ratio': '0.75',
                'processing_time': '5.2s',
                'worker_id': self.worker_id
            }
        }
        
        logger.info(f"{self.worker_name}: Resize completed for image {image_id}")
        return result


if __name__ == "__main__":
    worker = ResizeWorker()
    worker.start_consuming()
