"""Retry module - Service, worker, producer, consumer, queue, exchange, utils"""

import time
from app.shared.base.worker import BaseService, BaseWorker
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger
import json

logger = setup_logger(__name__)


class RetryService(BaseService):
    """Service for handling message retries"""
    
    def __init__(self):
        super().__init__("RetryService")
    
    def execute(self, message: dict) -> dict:
        """Handle retry task"""
        try:
            image_id = message.get("image_id")
            retry_count = message.get("retry_count", 0)
            
            self.logger.info(f"Retrying task for image {image_id}, attempt {retry_count}")
            time.sleep(2)
            
            return {
                "image_id": image_id,
                "status": "retried",
                "retry_count": retry_count
            }
        except Exception as e:
            self.logger.error(f"Error in retry service: {str(e)}")
            raise


class RetryWorker(BaseWorker):
    """Worker for handling retries"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.RETRY_QUEUE,
            worker_name="RetryWorker"
        )
        self.service = RetryService()
    
    def process(self, message: dict) -> dict:
        """Process retry task"""
        return self.service.execute(message)


def publish_retry_task(message: dict) -> bool:
    """Publish retry task"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.RETRY_QUEUE,
            body=json.dumps(message)
        )
        logger.info(f"Published retry task for image {message.get('image_id')}")
        return True
    except Exception as e:
        logger.error(f"Error publishing retry task: {str(e)}")
        return False


def setup_retry_queue():
    """Setup retry queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.RETRY_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.RETRY_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")


def start_retry_consumer():
    """Start retry consumer"""
    worker = RetryWorker()
    worker.start_consuming()


if __name__ == "__main__":
    start_retry_consumer()
