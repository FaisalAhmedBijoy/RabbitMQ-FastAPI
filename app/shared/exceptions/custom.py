"""
Custom Exceptions
Application-specific exception classes
"""


class ImageProcessingException(Exception):
    """Base exception for image processing errors"""
    pass


class RabbitMQConnectionError(ImageProcessingException):
    """Raised when RabbitMQ connection fails"""
    pass


class ImageQueueError(ImageProcessingException):
    """Raised when image cannot be queued"""
    pass


class InvalidImageError(ImageProcessingException):
    """Raised when image is invalid"""
    pass


class ProcessingError(ImageProcessingException):
    """Raised when image processing fails"""
    pass


class RetryError(ImageProcessingException):
    """Raised when retry operation fails"""
    pass


class DeadLetterError(ImageProcessingException):
    """Raised when message sent to DLQ"""
    pass
