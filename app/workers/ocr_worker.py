"""
OCR Worker - Handles OCR (Optical Character Recognition) processing
"""

import time
import random
from typing import Dict, Any

from app.core.config import RABBITMQ_CONFIG, APP_CONFIG
from app.shared.helpers.logger import setup_logger
from app.workers.base import BaseWorker

logger = setup_logger(__name__)


class OCRWorker(BaseWorker):
    """Worker for OCR text extraction"""
    
    def __init__(self, worker_id: int = 1):
        super().__init__(RABBITMQ_CONFIG.OCR_QUEUE, f"OCRWorker-{worker_id}")
        self.worker_id = worker_id
    
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate OCR processing
        
        Args:
            message: Image metadata message
        
        Returns:
            Processing result
        """
        image_id = message.get('image_id')
        filename = message.get('filename')
        
        logger.info(f"{self.worker_name}: Processing OCR for image {image_id} ({filename})")
        
        # Simulate random failure for demonstration
        if random.randint(1, 6) == 2:
            raise Exception(f"Simulated OCR processing failure for {filename}")
        
        # Simulate heavy processing with delay
        logger.info(f"{self.worker_name}: Extracting text from {filename}... (simulated)")
        time.sleep(7)  # Simulate longer OCR processing time
        
        # Simulate OCR results
        detected_texts = [
            "Vehicle Number ABC123",
            "License Plate: XYZ789",
            "Date: 2024-01-15",
        ]
        
        result = {
            'image_id': image_id,
            'task_type': 'ocr',
            'status': 'completed',
            'details': {
                'detected_text': detected_texts,
                'confidence': '0.92',
                'languages': ['English'],
                'processing_time': '7.5s',
                'worker_id': self.worker_id,
                'text_regions': 3
            }
        }
        
        logger.info(f"{self.worker_name}: OCR completed for image {image_id}. Detected {len(detected_texts)} text regions")
        return result


if __name__ == "__main__":
    worker = OCRWorker()
    worker.start_consuming()
