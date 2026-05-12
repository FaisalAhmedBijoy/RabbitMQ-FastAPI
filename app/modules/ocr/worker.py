"""OCR module - Service, worker, producer, consumer, queue, exchange, utils"""

import time
import random
from app.shared.base.worker import BaseService, BaseWorker
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger
import json

logger = setup_logger(__name__)


class OCRService(BaseService):
    """Service for OCR processing"""
    
    FAILURE_RATE = 6
    
    def __init__(self):
        super().__init__("OCRService")
    
    def execute(self, message: dict) -> dict:
        """Process OCR task"""
        try:
            image_id = message.get("image_id")
            processing_id = message.get("processing_id")
            
            self.logger.info(f"Processing OCR for image {image_id}")
            time.sleep(7)
            
            if random.randint(1, self.FAILURE_RATE) == 1:
                raise Exception(f"Simulated OCR failure for image {image_id}")
            
            return {
                "image_id": image_id,
                "processing_id": processing_id,
                "status": "completed",
                "text": "Sample OCR extracted text from image"
            }
        except Exception as e:
            self.logger.error(f"Error processing OCR: {str(e)}")
            raise


class OCRWorker(BaseWorker):
    """Worker for OCR processing"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.OCR_QUEUE,
            worker_name="OCRWorker"
        )
        self.service = OCRService()
    
    def process(self, message: dict) -> dict:
        """Process OCR task"""
        return self.service.execute(message)


def publish_ocr_task(message: dict) -> bool:
    """Publish OCR task"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.OCR_QUEUE,
            body=json.dumps(message)
        )
        logger.info(f"Published OCR task for image {message.get('image_id')}")
        return True
    except Exception as e:
        logger.error(f"Error publishing OCR task: {str(e)}")
        return False


def setup_ocr_queue():
    """Setup OCR queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.OCR_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.OCR_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")


def start_ocr_consumer():
    """Start OCR consumer"""
    worker = OCRWorker()
    worker.start_consuming()


if __name__ == "__main__":
    start_ocr_consumer()
