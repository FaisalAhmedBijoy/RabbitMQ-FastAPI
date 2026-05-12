"""
Logger Setup
Centralized logging configuration for the entire application
"""

import logging
import sys
from app.core.config import APP_CONFIG


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with consistent configuration
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(APP_CONFIG.LOG_LEVEL)
    
    return logger
