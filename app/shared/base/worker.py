"""
Base Worker Class
Abstract base class for all message queue workers
Implements common patterns: ACK/NACK, retry logic, dead letter handling
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional
import pika

from app.core.config import RABBITMQ_CONFIG
from app.core.rabbitmq import get_rabbitmq_channel
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


class BaseWorker(ABC):
    """Abstract base class for message queue workers"""
    
    def __init__(
        self,
        queue_name: str,
        worker_name: str,
        callback: Optional[Callable] = None
    ):
        """
        Initialize worker
        
        Args:
            queue_name: Name of the queue to consume from
            worker_name: Unique identifier for this worker
            callback: Optional callback function for custom processing
        """
        self.queue_name = queue_name
        self.worker_name = worker_name
        self.callback = callback
        self.channel = None
        self.retry_count = 0
    
    def connect(self):
        """Establish RabbitMQ connection"""
        try:
            self.channel = get_rabbitmq_channel()
            self.channel.basic_qos(prefetch_count=RABBITMQ_CONFIG.PREFETCH_COUNT)
            logger.info(f"{self.worker_name} connected to RabbitMQ")
        except Exception as e:
            logger.error(f"{self.worker_name} failed to connect: {str(e)}")
            raise
    
    def handle_message(
        self,
        ch: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes
    ):
        """
        Handle incoming message
        Implements ACK/NACK logic and error handling
        
        Args:
            ch: RabbitMQ channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            message = json.loads(body)
            logger.info(f"{self.worker_name} processing message: {message}")
            
            # Process message
            result = self.process(message)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"{self.worker_name} successfully processed message")
            
            return result
        
        except json.JSONDecodeError:
            logger.error(f"{self.worker_name} received invalid JSON")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        except Exception as e:
            logger.error(f"{self.worker_name} error processing message: {str(e)}")
            
            # Check retry count
            if "retry_count" not in message:
                message["retry_count"] = 0
            
            if message.get("retry_count", 0) < RABBITMQ_CONFIG.MAX_RETRIES:
                # Requeue message for retry
                self.requeue_message(ch, method, message)
            else:
                # Send to dead letter queue
                self.send_to_dlq(ch, method, message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
    
    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message
        Must be implemented by subclasses
        
        Args:
            message: Message data
            
        Returns:
            Processing result
        """
        pass
    
    def requeue_message(
        self,
        ch: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        message: Dict[str, Any]
    ):
        """
        Requeue message for retry
        
        Args:
            ch: RabbitMQ channel
            method: Delivery method
            message: Message data
        """
        try:
            message["retry_count"] = message.get("retry_count", 0) + 1
            logger.info(f"Requeuing message, retry count: {message['retry_count']}")
            
            # Wait before retrying
            time.sleep(RABBITMQ_CONFIG.RETRY_DELAY / 1000)
            
            # Publish back to retry queue
            ch.basic_publish(
                exchange="",
                routing_key=RABBITMQ_CONFIG.RETRY_QUEUE,
                body=json.dumps(message)
            )
            
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        except Exception as e:
            logger.error(f"Error requeuing message: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def send_to_dlq(
        self,
        ch: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        message: Dict[str, Any]
    ):
        """
        Send message to dead letter queue
        
        Args:
            ch: RabbitMQ channel
            method: Delivery method
            message: Message data
        """
        try:
            message["dlq_reason"] = "Max retries exceeded"
            logger.info(f"Sending message to DLQ: {message}")
            
            ch.basic_publish(
                exchange="",
                routing_key=RABBITMQ_CONFIG.DEAD_LETTER_QUEUE,
                body=json.dumps(message)
            )
        
        except Exception as e:
            logger.error(f"Error sending to DLQ: {str(e)}")
    
    def start_consuming(self):
        """Start consuming messages from queue"""
        try:
            self.connect()
            
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.handle_message
            )
            
            logger.info(f"{self.worker_name} started consuming from {self.queue_name}")
            self.channel.start_consuming()
        
        except KeyboardInterrupt:
            logger.info(f"{self.worker_name} stopped")
            self.channel.stop_consuming()
            self.channel.connection.close()
        
        except Exception as e:
            logger.error(f"{self.worker_name} fatal error: {str(e)}")
            raise


class BaseService(ABC):
    """Abstract base class for services"""
    
    def __init__(self, name: str):
        """
        Initialize service
        
        Args:
            name: Service name
        """
        self.name = name
        self.logger = setup_logger(f"{self.__class__.__name__}.{name}")
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute service logic"""
        pass
