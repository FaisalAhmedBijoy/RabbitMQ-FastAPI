"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_message():
    """Fixture: Sample message for testing"""
    return {
        "image_id": 123,
        "image_path": "/path/to/image.jpg",
        "processing_id": "test-uuid-1234",
        "filename": "image.jpg",
        "image_size": 1024000
    }


@pytest.fixture
def mock_rabbitmq_channel():
    """Fixture: Mock RabbitMQ channel"""
    from unittest.mock import MagicMock
    channel = MagicMock()
    channel.is_closed = False
    return channel


@pytest.fixture
def mock_rabbitmq_connection(mock_rabbitmq_channel):
    """Fixture: Mock RabbitMQ connection"""
    from unittest.mock import MagicMock
    connection = MagicMock()
    connection.channel.return_value = mock_rabbitmq_channel
    connection.is_closed = False
    return connection
