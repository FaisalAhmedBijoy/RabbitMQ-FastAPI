"""
Application Configuration
Centralized configuration management for the entire application
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RabbitMQConfig:
    """RabbitMQ Configuration"""
    HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    PORT: int = int(os.getenv("RABBITMQ_PORT", 5672))
    USER: str = os.getenv("RABBITMQ_USER", "guest")
    PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    VHOST: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # Queue Configuration
    RESIZE_QUEUE = "resize_queue"
    THUMBNAIL_QUEUE = "thumbnail_queue"
    OCR_QUEUE = "ocr_queue"
    AI_TAGGING_QUEUE = "ai_tagging_queue"
    RETRY_QUEUE = "retry_queue"
    DEAD_LETTER_QUEUE = "dead_letter_queue"
    LOGGING_QUEUE = "logging_queue"
    
    # Exchange Configuration
    DIRECT_EXCHANGE = "image_processing_direct"
    FANOUT_EXCHANGE = "image_processing_fanout"
    TOPIC_EXCHANGE = "image_processing_topic"
    
    # Worker Configuration
    PREFETCH_COUNT = 1
    MAX_RETRIES = 3
    RETRY_DELAY = 10000  # milliseconds

    def get_connection_string(self) -> str:
        """Build RabbitMQ connection string"""
        return f"amqp://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.VHOST}"


@dataclass
class DatabaseConfig:
    """Database Configuration"""
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./image_processing.db"
    )
    ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"


@dataclass
class AppConfig:
    """Application Configuration"""
    APP_NAME: str = "Async Image Processing Pipeline"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Upload Configuration
    UPLOAD_DIR: str = "app/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Processing timeouts (in seconds)
    RESIZE_TIMEOUT: int = 30
    THUMBNAIL_TIMEOUT: int = 20
    OCR_TIMEOUT: int = 60
    AI_TAGGING_TIMEOUT: int = 45
    
    # API Configuration
    API_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("FASTAPI_PORT", 8000))


@dataclass
class SecurityConfig:
    """Security Configuration"""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Global config instances
RABBITMQ_CONFIG = RabbitMQConfig()
DATABASE_CONFIG = DatabaseConfig()
APP_CONFIG = AppConfig()
SECURITY_CONFIG = SecurityConfig()
