"""
Application Constants
Centralized constants used throughout the application
"""

# Processing Status
class ProcessingStatus:
    """Processing status constants"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTERED = "dead_lettered"


# Task Types
class TaskType:
    """Task type constants"""
    RESIZE = "resize"
    THUMBNAIL = "thumbnail"
    OCR = "ocr"
    AI_TAGGING = "ai_tagging"


# Message Status
class MessageStatus:
    """Message status in queue"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DLQ = "dead_letter_queue"


# Error Messages
class ErrorMessages:
    """Standard error messages"""
    CONNECTION_ERROR = "Failed to connect to RabbitMQ"
    INVALID_IMAGE_ID = "image_id must be positive"
    FAILED_TO_QUEUE = "Failed to queue image for processing"
    INVALID_REQUEST = "Invalid request data"
    INTERNAL_ERROR = "Internal server error"


# Success Messages
class SuccessMessages:
    """Standard success messages"""
    IMAGE_QUEUED = "Image processing started"
    PROCESSING_COMPLETE = "Processing completed successfully"
    RETRY_SUCCESSFUL = "Retry successful"


# Processing Delays (simulated, in seconds)
class ProcessingDelays:
    """Simulated processing delays"""
    RESIZE_DELAY = 5
    THUMBNAIL_DELAY = 3
    OCR_DELAY = 7
    AI_TAGGING_DELAY = 6


# Failure Rates (1 in N)
class FailureRates:
    """Simulated failure rates (1 in N chance)"""
    RESIZE_FAILURE_RATE = 10
    THUMBNAIL_FAILURE_RATE = 8
    OCR_FAILURE_RATE = 6
    AI_TAGGING_FAILURE_RATE = 7
