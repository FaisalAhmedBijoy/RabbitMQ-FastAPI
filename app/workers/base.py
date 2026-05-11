"""
Base Worker class for all RabbitMQ consumers
"""

import json
import pika
import time
import random
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any
from datetime import datetime

from app.rabbitmq import get_rabbitmq_channel
from app.config import RABBITMQ_CONFIG, APP_CONFIG
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseWorker(ABC):
    """Base class for all RabbitMQ workers"""
    
    def __init__(self, queue_name: str, worker_name: str):
        """
        Initialize worker
        
        Args:
            queue_name: Name of the queue to consume from
            worker_name: Friendly name for this worker
        """
        self.queue_name = queue_name
        self.worker_name = worker_name
        self.channel = None
    
    def connect(self):
        """Connect to RabbitMQ"""
        self.channel = get_rabbitmq_channel()
        # Set fair dispatch
        self.channel.basic_qos(prefetch_count=RABBITMQ_CONFIG.PREFETCH_COUNT)
        logger.info(f"{self.worker_name} connected to RabbitMQ")
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a message from the queue
        
        Args:
            message: Message data
        
        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            result = self.process(message)
            logger.info(f"{self.worker_name}: Successfully processed image {message.get('image_id')}: {result}")
            return True
        except Exception as e:
            logger.error(f"{self.worker_name}: Error processing image {message.get('image_id')}: {str(e)}")
            return False
    
    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the image
        
        Override this method in subclasses
        
        Args:
            message: Message data containing image info
        
        Returns:
            Processing result
        """
        pass
    
    def handle_message(self, ch, method, properties, body):
        """
        Handle incoming message from RabbitMQ
        
        Implements ACK/NACK logic
        """
        try:
            message = json.loads(body.decode('utf-8'))
            logger.info(f"{self.worker_name}: Received message for image {message.get('image_id')}")
            
            # Process the message
            success = self.process_message(message)
            
            if success:
                # ACK - Message processed successfully
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"{self.worker_name}: ACKed message for image {message.get('image_id')}")
            else:
                # NACK - Message processing failed
                retry_count = message.get('retry_count', 0)
                
                if retry_count < RABBITMQ_CONFIG.MAX_RETRIES:
                    # Requeue the message with incremented retry count
                    message['retry_count'] = retry_count + 1
                    self.requeue_message(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"{self.worker_name}: Requeued message for image {message.get('image_id')} (retry {retry_count + 1})")
                else:
                    # Max retries exceeded - send to DLQ
                    self.send_to_dlq(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.error(f"{self.worker_name}: Sent message for image {message.get('image_id')} to DLQ after {retry_count} retries")
        
        except json.JSONDecodeError as e:
            logger.error(f"{self.worker_name}: JSON decode error: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"{self.worker_name}: Unexpected error: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def requeue_message(self, message: Dict[str, Any]):
        """
        Requeue a message after delay
        
        Args:
            message: Message to requeue
        """
        try:
            self.channel.basic_publish(
                exchange=RABBITMQ_CONFIG.DIRECT_EXCHANGE,
                routing_key='retry',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
        except Exception as e:
            logger.error(f"Error requeuing message: {str(e)}")
    
    def send_to_dlq(self, message: Dict[str, Any]):
        """
        Send a message to Dead Letter Queue
        
        Args:
            message: Message to send to DLQ
        """
        try:
            self.channel.basic_publish(
                exchange=RABBITMQ_CONFIG.DIRECT_EXCHANGE,
                routing_key='dlq',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
        except Exception as e:
            logger.error(f"Error sending to DLQ: {str(e)}")
    
    def start_consuming(self):
        """Start consuming messages from the queue"""
        try:
            self.connect()
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.handle_message
            )
            logger.info(f"{self.worker_name} started consuming from {self.queue_name}")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info(f"{self.worker_name} stopped by user")
            self.channel.stop_consuming()
            self.channel.connection.close()
        except Exception as e:
            logger.error(f"Error in start_consuming: {str(e)}")
            raise
