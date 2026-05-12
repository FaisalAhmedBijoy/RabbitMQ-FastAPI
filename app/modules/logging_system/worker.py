"""Logging System module - Service, worker, producer, consumer, queue, exchange, utils"""

import time
from app.shared.base.worker import BaseService, BaseWorker
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger
import json

logger = setup_logger(__name__)


class LoggingService(BaseService):
    """Service for centralized logging"""
    
    def __init__(self):
        super().__init__("LoggingService")
    
    def execute(self, message: dict) -> dict:
        """Handle logging message"""
        try:
            log_level = message.get("level", "INFO")
            log_message = message.get("message", "")
            image_id = message.get("image_id")
            
            self.logger.log(
                getattr(logger, log_level.lower(), 20),
                f"[Image {image_id}] {log_message}"
            )
            
            return {
                "status": "logged",
                "image_id": image_id
            }
        except Exception as e:
            self.logger.error(f"Error in logging service: {str(e)}")
            raise


class LoggingWorker(BaseWorker):
    """Worker for centralized logging"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.LOGGING_QUEUE,
            worker_name="LoggingWorker"
        )
        self.service = LoggingService()
    
    def process(self, message: dict) -> dict:
        """Process logging message"""
        return self.service.execute(message)


def publish_log(message: dict) -> bool:
    """Publish log message"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.LOGGING_QUEUE,
            body=json.dumps(message)
        )
        return True
    except Exception as e:
        logger.error(f"Error publishing log: {str(e)}")
        return False


def setup_logging_queue():
    """Setup logging queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.LOGGING_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.LOGGING_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")


def start_logging_consumer():
    """Start logging consumer"""
    worker = LoggingWorker()
    worker.start_consuming()


if __name__ == "__main__":
    start_logging_consumer()
