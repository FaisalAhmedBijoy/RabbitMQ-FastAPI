"""Resize Exchange Setup"""

from app.core.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


def setup_resize_exchange():
    """Setup resize exchange"""
    try:
        channel = get_rabbitmq_channel()
        channel.exchange_declare(
            exchange=RABBITMQ_CONFIG.DIRECT_EXCHANGE,
            exchange_type="direct",
            durable=True
        )
        logger.info(f"Exchange {RABBITMQ_CONFIG.DIRECT_EXCHANGE} declared")
    except Exception as e:
        logger.error(f"Error declaring exchange: {str(e)}")
