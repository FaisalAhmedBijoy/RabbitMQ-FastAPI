"""Dead Letter module - Service, worker, producer, consumer, queue, exchange, utils"""

import time
from app.shared.base.worker import BaseService, BaseWorker
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger
import json

logger = setup_logger(__name__)


class DeadLetterService(BaseService):
    """Service for handling dead letter queue messages"""
    
    def __init__(self):
        super().__init__("DeadLetterService")
    
    def execute(self, message: dict) -> dict:
        """Handle dead letter message"""
        try:
            image_id = message.get("image_id")
            dlq_reason = message.get("dlq_reason", "Unknown")
            
            self.logger.error(f"Message in DLQ for image {image_id}: {dlq_reason}")
            
            return {
                "image_id": image_id,
                "status": "dead_lettered",
                "reason": dlq_reason
            }
        except Exception as e:
            self.logger.error(f"Error in DLQ service: {str(e)}")
            raise


class DeadLetterWorker(BaseWorker):
    """Worker for handling dead letter messages"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.DEAD_LETTER_QUEUE,
            worker_name="DeadLetterWorker"
        )
        self.service = DeadLetterService()
    
    def process(self, message: dict) -> dict:
        """Process dead letter message"""
        return self.service.execute(message)


def publish_to_dlq(message: dict) -> bool:
    """Publish message to DLQ"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.DEAD_LETTER_QUEUE,
            body=json.dumps(message)
        )
        logger.info(f"Published message to DLQ for image {message.get('image_id')}")
        return True
    except Exception as e:
        logger.error(f"Error publishing to DLQ: {str(e)}")
        return False


def setup_dlq():
    """Setup dead letter queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.DEAD_LETTER_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.DEAD_LETTER_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")


def start_dlq_consumer():
    """Start DLQ consumer"""
    worker = DeadLetterWorker()
    worker.start_consuming()


if __name__ == "__main__":
    start_dlq_consumer()
