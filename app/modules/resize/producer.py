"""Resize Producer"""

import json
from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


def publish_resize_task(message: dict) -> bool:
    """Publish resize task"""
    try:
        channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_CONFIG.RESIZE_QUEUE,
            body=json.dumps(message)
        )
        logger.info(f"Published resize task for image {message.get('image_id')}")
        return True
    except Exception as e:
        logger.error(f"Error publishing resize task: {str(e)}")
        return False
