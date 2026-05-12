"""Resize Queue Setup"""

from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


def setup_resize_queue():
    """Setup resize queue"""
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG.RESIZE_QUEUE,
            durable=True
        )
        logger.info(f"Queue {RABBITMQ_CONFIG.RESIZE_QUEUE} declared")
    except Exception as e:
        logger.error(f"Error declaring queue: {str(e)}")
