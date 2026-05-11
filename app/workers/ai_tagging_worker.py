"""
AI Tagging Worker - Handles AI-based image tagging and object classification
"""

import time
import random
from typing import Dict, Any

from app.config import RABBITMQ_CONFIG, APP_CONFIG
from app.utils.logger import setup_logger
from app.workers.base import BaseWorker

logger = setup_logger(__name__)


class AITaggingWorker(BaseWorker):
    """Worker for AI-based image tagging"""
    
    def __init__(self, worker_id: int = 1):
        super().__init__(RABBITMQ_CONFIG.AI_TAGGING_QUEUE, f"AITaggingWorker-{worker_id}")
        self.worker_id = worker_id
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate AI tagging and classification
        
        Args:
            message: Image metadata message
        
        Returns:
            Processing result
        """
        image_id = message.get('image_id')
        filename = message.get('filename')
        
        logger.info(f"{self.worker_name}: Processing AI tagging for image {image_id} ({filename})")
        
        # Simulate random failure for demonstration
        if random.randint(1, 7) == 4:
            raise Exception(f"Simulated AI tagging failure for {filename}")
        
        # Simulate heavy AI processing with delay
        logger.info(f"{self.worker_name}: Running AI model on {filename}... (simulated)")
        time.sleep(6)  # Simulate AI processing time
        
        # Simulate AI tagging results
        tags = ['vehicle', 'car', 'road', 'outdoor', 'transportation']
        object_detections = {
            'car': 0.94,
            'road': 0.87,
            'sky': 0.76,
            'building': 0.65
        }
        
        result = {
            'image_id': image_id,
            'task_type': 'ai_tagging',
            'status': 'completed',
            'details': {
                'tags': tags,
                'objects_detected': object_detections,
                'overall_confidence': '0.85',
                'processing_time': '6.3s',
                'worker_id': self.worker_id,
                'model_version': '2.1'
            }
        }
        
        logger.info(f"{self.worker_name}: AI tagging completed for image {image_id}. Detected {len(tags)} tags")
        return result


if __name__ == "__main__":
    worker = AITaggingWorker()
    worker.start_consuming()
