"""
RabbitMQ Producer - Publishes messages to queues
"""

import json
import pika
from datetime import datetime
from typing import Dict, Any

from app.rabbitmq import get_rabbitmq_channel
from app.config import RABBITMQ_CONFIG
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageProcessingProducer:
    """Publishes image processing tasks to RabbitMQ"""
    
    @staticmethod
    def publish_image(image_data: Dict[str, Any]) -> bool:
        """
        Publish image to all processing queues
        
        Args:
            image_data: Image metadata dictionary
        
        Returns:
            True if published successfully, False otherwise
        """
        try:
            channel = get_rabbitmq_channel()
            
            # Add timestamp and retry count
            message_data = {
                **image_data,
                'retry_count': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            message_body = json.dumps(message_data)
            
            # Publish to all processing queues
            queues_and_routing_keys = [
                (RABBITMQ_CONFIG.RESIZE_QUEUE, 'resize'),
                (RABBITMQ_CONFIG.THUMBNAIL_QUEUE, 'thumbnail'),
                (RABBITMQ_CONFIG.OCR_QUEUE, 'ocr'),
                (RABBITMQ_CONFIG.AI_TAGGING_QUEUE, 'ai_tagging'),
            ]
            
            for queue_name, routing_key in queues_and_routing_keys:
                try:
                    channel.basic_publish(
                        exchange=RABBITMQ_CONFIG.DIRECT_EXCHANGE,
                        routing_key=routing_key,
                        body=message_body,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # Make message persistent
                            content_type='application/json'
                        )
                    )
                    logger.info(f"Published message to {queue_name}: image_id={image_data.get('image_id')}")
                
                except Exception as e:
                    logger.error(f"Error publishing to {queue_name}: {str(e)}")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error in publish_image: {str(e)}")
            return False


def publish_image_task(image_id: int, filename: str, image_path: str, image_size: str) -> bool:
    """
    Publish image task to processing queues
    
    Args:
        image_id: Unique image identifier
        filename: Original filename
        image_path: Path to image
        image_size: Image size
    
    Returns:
        True if successful
    """
    image_data = {
        'image_id': image_id,
        'filename': filename,
        'image_path': image_path,
        'image_size': image_size,
    }
    
    return ImageProcessingProducer.publish_image(image_data)
