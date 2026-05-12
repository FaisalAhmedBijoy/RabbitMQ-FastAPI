"""Thumbnail module - Service, worker, producer, consumer, queue, exchange, utils"""

import time
import random
from app.shared.base.worker import BaseService, BaseWorker
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger
import json

logger = setup_logger(__name__)


class ThumbnailService(BaseService):
    """Service for generating thumbnails"""
    
    FAILURE_RATE = 8
    
    def __init__(self):
        super().__init__("ThumbnailService")
    
    def execute(self, message: dict) -> dict:
        """Generate thumbnail"""
        try:
            image_id = message.get("image_id")
            processing_id = message.get("processing_id")
            
            self.logger.info(f"Generating thumbnail for image {image_id}")
            time.sleep(3)
            
            if random.randint(1, self.FAILURE_RATE) == 1:
                raise Exception(f"Simulated thumbnail failure for image {image_id}")
            
            return {
                "image_id": image_id,
                "processing_id": processing_id,
                "status": "completed",
                "output_path": f"app/uploads/thumbnails/{image_id}_thumb.jpg"
            }
        except Exception as e:
            self.logger.error(f"Error generating thumbnail: {str(e)}")
            raise


class ThumbnailWorker(BaseWorker):
    """Worker for thumbnail generation"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.THUMBNAIL_QUEUE,
            worker_name="ThumbnailWorker"
        )
        self.service = ThumbnailService()
    
    def process(self, message: dict) -> dict:
        """Process thumbnail task"""
        return self.service.execute(message)


def publish_thumbnail_task(message: dict) -> bool:
    """Publish thumbnail task"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.THUMBNAIL_QUEUE,
            body=json.dumps(message)
        )
        logger.info(f"Published thumbnail task for image {message.get('image_id')}")
        return True
    except Exception as e:
        logger.error(f"Error publishing thumbnail task: {str(e)}")
        return False


def setup_thumbnail_queue():
    """Setup thumbnail queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.THUMBNAIL_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.THUMBNAIL_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")


def start_thumbnail_consumer():
    """Start thumbnail consumer"""
    worker = ThumbnailWorker()
    worker.start_consuming()


if __name__ == "__main__":
    start_thumbnail_consumer()
