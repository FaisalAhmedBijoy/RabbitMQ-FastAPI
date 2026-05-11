"""RabbitMQ package"""

from app.rabbitmq.connection import (
    RabbitMQConnection,
    get_rabbitmq_channel,
    get_rabbitmq_connection,
)

__all__ = [
    "RabbitMQConnection",
    "get_rabbitmq_channel",
    "get_rabbitmq_connection",
]
