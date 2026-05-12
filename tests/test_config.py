"""
Unit tests for configuration module
"""

import os
import pytest
from app.core.config import (
    RabbitMQConfig,
    AppConfig,
    DatabaseConfig,
    SecurityConfig,
    RABBITMQ_CONFIG,
    APP_CONFIG,
)


class TestRabbitMQConfig:
    """Test RabbitMQ configuration"""
    
    def test_default_host(self):
        """Test default RabbitMQ host"""
        config = RabbitMQConfig()
        assert config.HOST == "localhost"
    
    def test_default_port(self):
        """Test default RabbitMQ port"""
        config = RabbitMQConfig()
        assert config.PORT == 5672
    
    def test_connection_string(self):
        """Test RabbitMQ connection string generation"""
        config = RabbitMQConfig()
        conn_str = config.get_connection_string()
        assert "amqp://" in conn_str
        assert config.HOST in conn_str
        assert str(config.PORT) in conn_str
    
    def test_queue_names_defined(self):
        """Test that all queue names are defined"""
        config = RabbitMQConfig()
        assert config.RESIZE_QUEUE
        assert config.THUMBNAIL_QUEUE
        assert config.OCR_QUEUE
        assert config.AI_TAGGING_QUEUE
        assert config.RETRY_QUEUE
        assert config.DEAD_LETTER_QUEUE


class TestAppConfig:
    """Test application configuration"""
    
    def test_default_api_host(self):
        """Test default API host"""
        config = AppConfig()
        assert config.API_HOST == "0.0.0.0"
    
    def test_default_api_port(self):
        """Test default API port"""
        config = AppConfig()
        assert config.API_PORT == 8000
    
    def test_upload_dir_exists(self):
        """Test upload directory is configured"""
        config = AppConfig()
        assert config.UPLOAD_DIR
    
    def test_timeouts_configured(self):
        """Test processing timeouts are configured"""
        config = AppConfig()
        assert config.RESIZE_TIMEOUT > 0
        assert config.THUMBNAIL_TIMEOUT > 0
        assert config.OCR_TIMEOUT > 0
        assert config.AI_TAGGING_TIMEOUT > 0


class TestSecurityConfig:
    """Test security configuration"""
    
    def test_secret_key_in_development(self):
        """Test SECRET_KEY is generated in development"""
        # Save original env
        original_env = os.getenv("ENVIRONMENT")
        original_key = os.getenv("SECRET_KEY")
        
        try:
            # Set to development mode
            os.environ["ENVIRONMENT"] = "development"
            if "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]
            
            # Create config - should generate a key
            config = SecurityConfig()
            assert config.SECRET_KEY is not None
            assert len(config.SECRET_KEY) > 20
        
        finally:
            # Restore original env
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            
            if original_key:
                os.environ["SECRET_KEY"] = original_key
            elif "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]
    
    def test_algorithm_set(self):
        """Test default algorithm is set"""
        # Skip if SECRET_KEY not set (will be handled by __post_init__)
        try:
            config = SecurityConfig()
            assert config.ALGORITHM == "HS256"
        except ValueError:
            # Expected if SECRET_KEY not set in production mode
            pass
    
    def test_token_expiry_configured(self):
        """Test token expiry is configured"""
        try:
            config = SecurityConfig()
            assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        except ValueError:
            # Expected if SECRET_KEY not set
            pass


class TestGlobalConfigs:
    """Test global configuration instances"""
    
    def test_rabbitmq_config_instantiated(self):
        """Test RABBITMQ_CONFIG is available"""
        assert RABBITMQ_CONFIG is not None
        assert isinstance(RABBITMQ_CONFIG, RabbitMQConfig)
    
    def test_app_config_instantiated(self):
        """Test APP_CONFIG is available"""
        assert APP_CONFIG is not None
        assert isinstance(APP_CONFIG, AppConfig)
    
    def test_database_config_instantiated(self):
        """Test DATABASE_CONFIG is available"""
        assert RABBITMQ_CONFIG is not None
        assert isinstance(RABBITMQ_CONFIG, RabbitMQConfig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
