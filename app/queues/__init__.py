"""
Queue declarations and management
"""

from app.rabbitmq import get_rabbitmq_channel
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


def declare_queues():
    """Declare all required queues with durable settings"""
    channel = get_rabbitmq_channel()
    
    queues = [
        RABBITMQ_CONFIG.RESIZE_QUEUE,
        RABBITMQ_CONFIG.THUMBNAIL_QUEUE,
        RABBITMQ_CONFIG.OCR_QUEUE,
        RABBITMQ_CONFIG.AI_TAGGING_QUEUE,
        RABBITMQ_CONFIG.RETRY_QUEUE,
        RABBITMQ_CONFIG.DEAD_LETTER_QUEUE,
        RABBITMQ_CONFIG.LOGGING_QUEUE,
    ]
    
    for queue_name in queues:
        try:
            # Declare durable queue
            channel.queue_declare(
                queue=queue_name,
                durable=True,
                auto_delete=False
            )
            logger.info(f"Declared queue: {queue_name}")
        except Exception as e:
            logger.error(f"Error declaring queue {queue_name}: {str(e)}")
            raise


def declare_exchanges():
    """Declare all required exchanges"""
    channel = get_rabbitmq_channel()
    
    # Direct exchange
    try:
        channel.exchange_declare(
            exchange=RABBITMQ_CONFIG.DIRECT_EXCHANGE,
            exchange_type='direct',
            durable=True
        )
        logger.info(f"Declared direct exchange: {RABBITMQ_CONFIG.DIRECT_EXCHANGE}")
    except Exception as e:
        logger.error(f"Error declaring direct exchange: {str(e)}")
    
    # Fanout exchange
    try:
        channel.exchange_declare(
            exchange=RABBITMQ_CONFIG.FANOUT_EXCHANGE,
            exchange_type='fanout',
            durable=True
        )
        logger.info(f"Declared fanout exchange: {RABBITMQ_CONFIG.FANOUT_EXCHANGE}")
    except Exception as e:
        logger.error(f"Error declaring fanout exchange: {str(e)}")
    
    # Topic exchange
    try:
        channel.exchange_declare(
            exchange=RABBITMQ_CONFIG.TOPIC_EXCHANGE,
            exchange_type='topic',
            durable=True
        )
        logger.info(f"Declared topic exchange: {RABBITMQ_CONFIG.TOPIC_EXCHANGE}")
    except Exception as e:
        logger.error(f"Error declaring topic exchange: {str(e)}")


def bind_queues():
    """Bind queues to exchanges"""
    channel = get_rabbitmq_channel()
    
    bindings = [
        (RABBITMQ_CONFIG.RESIZE_QUEUE, RABBITMQ_CONFIG.DIRECT_EXCHANGE, 'resize'),
        (RABBITMQ_CONFIG.THUMBNAIL_QUEUE, RABBITMQ_CONFIG.DIRECT_EXCHANGE, 'thumbnail'),
        (RABBITMQ_CONFIG.OCR_QUEUE, RABBITMQ_CONFIG.DIRECT_EXCHANGE, 'ocr'),
        (RABBITMQ_CONFIG.AI_TAGGING_QUEUE, RABBITMQ_CONFIG.DIRECT_EXCHANGE, 'ai_tagging'),
        (RABBITMQ_CONFIG.RETRY_QUEUE, RABBITMQ_CONFIG.DIRECT_EXCHANGE, 'retry'),
        (RABBITMQ_CONFIG.LOGGING_QUEUE, RABBITMQ_CONFIG.FANOUT_EXCHANGE, ''),
        (RABBITMQ_CONFIG.DEAD_LETTER_QUEUE, RABBITMQ_CONFIG.DIRECT_EXCHANGE, 'dlq'),
    ]
    
    for queue_name, exchange_name, routing_key in bindings:
        try:
            channel.queue_bind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key
            )
            logger.info(f"Bound queue {queue_name} to exchange {exchange_name} with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Error binding queue {queue_name}: {str(e)}")


def setup_rabbitmq():
    """Initialize RabbitMQ infrastructure"""
    logger.info("Setting up RabbitMQ infrastructure...")
    declare_exchanges()
    declare_queues()
    bind_queues()
    logger.info("RabbitMQ infrastructure setup complete")
