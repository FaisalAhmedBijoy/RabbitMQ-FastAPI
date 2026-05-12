"""
RabbitMQ Connection and Configuration Management
Handles all RabbitMQ connection, channel creation, and infrastructure setup
"""

import pika
from typing import Optional
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


class RabbitMQConnection:
    """Manages RabbitMQ connection and channels"""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
    
    def connect(self) -> pika.adapters.blocking_connection.BlockingChannel:
        """
        Establish connection to RabbitMQ
        
        Returns:
            RabbitMQ channel
        """
        try:
            credentials = pika.PlainCredentials(
                RABBITMQ_CONFIG.USER,
                RABBITMQ_CONFIG.PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_CONFIG.HOST,
                port=RABBITMQ_CONFIG.PORT,
                virtual_host=RABBITMQ_CONFIG.VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"Connected to RabbitMQ at {RABBITMQ_CONFIG.HOST}:{RABBITMQ_CONFIG.PORT}")
            return self.channel
        
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise
    
    def disconnect(self):
        """Close RabbitMQ connection"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {str(e)}")
    
    def get_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        """Get existing channel or create new connection"""
        if self.channel is None or self.channel.is_closed:
            self.connect()
        return self.channel


# Global connection instance
_rabbitmq_connection = RabbitMQConnection()


def get_rabbitmq_channel() -> pika.adapters.blocking_connection.BlockingChannel:
    """Get RabbitMQ channel"""
    return _rabbitmq_connection.get_channel()


def get_rabbitmq_connection() -> RabbitMQConnection:
    """Get RabbitMQ connection manager"""
    return _rabbitmq_connection
