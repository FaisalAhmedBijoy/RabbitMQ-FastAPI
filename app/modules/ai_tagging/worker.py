"""AI Tagging module - Service, worker, producer, consumer, queue, exchange, utils"""

import time
import random
from app.shared.base.worker import BaseService, BaseWorker
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger
import json

logger = setup_logger(__name__)


class AITaggingService(BaseService):
    """Service for AI tagging"""
    
    FAILURE_RATE = 7
    
    def __init__(self):
        super().__init__("AITaggingService")
    
    def execute(self, message: dict) -> dict:
        """Process AI tagging task"""
        try:
            image_id = message.get("image_id")
            processing_id = message.get("processing_id")
            
            self.logger.info(f"Processing AI tagging for image {image_id}")
            time.sleep(6)
            
            if random.randint(1, self.FAILURE_RATE) == 1:
                raise Exception(f"Simulated AI tagging failure for image {image_id}")
            
            return {
                "image_id": image_id,
                "processing_id": processing_id,
                "status": "completed",
                "tags": ["landscape", "nature", "sunset", "quality"]
            }
        except Exception as e:
            self.logger.error(f"Error processing AI tagging: {str(e)}")
            raise


class AITaggingWorker(BaseWorker):
    """Worker for AI tagging"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.AI_TAGGING_QUEUE,
            worker_name="AITaggingWorker"
        )
        self.service = AITaggingService()
    
    def process(self, message: dict) -> dict:
        """Process AI tagging task"""
        return self.service.execute(message)


def publish_ai_tagging_task(message: dict) -> bool:
    """Publish AI tagging task"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.AI_TAGGING_QUEUE,
            body=json.dumps(message)
        )
        logger.info(f"Published AI tagging task for image {message.get('image_id')}")
        return True
    except Exception as e:
        logger.error(f"Error publishing AI tagging task: {str(e)}")
        return False


def setup_ai_tagging_queue():
    """Setup AI tagging queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.AI_TAGGING_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.AI_TAGGING_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")


def start_ai_tagging_consumer():
    """Start AI tagging consumer"""
    worker = AITaggingWorker()
    worker.start_consuming()


if __name__ == "__main__":
    start_ai_tagging_consumer()
