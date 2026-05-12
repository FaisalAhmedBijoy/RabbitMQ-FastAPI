"""
RabbitMQ connection and channel management

DEPRECATED: This file is deprecated. Use app.core.rabbitmq instead.
This file is kept for backwards compatibility only.
"""

# For backwards compatibility, re-export from the canonical location
from app.core.rabbitmq import (
    RabbitMQConnection,
    get_rabbitmq_channel,
    get_rabbitmq_connection,
    _rabbitmq_connection,
)

__all__ = [
    "RabbitMQConnection",
    "get_rabbitmq_channel",
    "get_rabbitmq_connection",
]
    return _rabbitmq_connection
