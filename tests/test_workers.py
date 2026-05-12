"""
Unit tests for worker modules
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.workers.base import BaseWorker


class MockWorker(BaseWorker):
    """Concrete implementation of BaseWorker for testing"""
    
    def process(self, message):
        """Mock process implementation"""
        return {"status": "success", "image_id": message.get("image_id")}


class TestBaseWorker:
    """Test BaseWorker class"""
    
    def test_worker_initialization(self):
        """Test worker can be initialized"""
        worker = MockWorker("test_queue", "TestWorker-1")
        assert worker.queue_name == "test_queue"
        assert worker.worker_name == "TestWorker-1"
        assert worker.channel is None
    
    def test_process_message_success(self):
        """Test successful message processing"""
        worker = MockWorker("test_queue", "TestWorker-1")
        message = {"image_id": 123, "filename": "test.jpg"}
        
        result = worker.process_message(message)
        assert result is True
    
    def test_process_message_failure(self):
        """Test failed message processing"""
        worker = MockWorker("test_queue", "TestWorker-1")
        
        # Patch process to raise exception
        with patch.object(worker, "process", side_effect=Exception("Test error")):
            message = {"image_id": 123}
            result = worker.process_message(message)
            assert result is False
    
    def test_worker_name_includes_id(self):
        """Test worker name includes worker ID"""
        worker = MockWorker("resize_queue", "ResizeWorker-5")
        assert "ResizeWorker" in worker.worker_name
        assert "5" in worker.worker_name
    
    @patch("app.workers.base.get_rabbitmq_channel")
    def test_connect_sets_channel(self, mock_get_channel):
        """Test connect method sets channel"""
        mock_channel = MagicMock()
        mock_get_channel.return_value = mock_channel
        
        worker = MockWorker("test_queue", "TestWorker-1")
        worker.connect()
        
        assert worker.channel is not None
        mock_channel.basic_qos.assert_called_once()
    
    def test_process_returns_dict(self):
        """Test process returns dictionary"""
        worker = MockWorker("test_queue", "TestWorker-1")
        message = {"image_id": 123}
        
        result = worker.process(message)
        assert isinstance(result, dict)
        assert "status" in result


class TestWorkerIntegration:
    """Integration tests for workers"""
    
    def test_multiple_workers_can_exist(self):
        """Test multiple worker instances can coexist"""
        worker1 = MockWorker("queue1", "Worker-1")
        worker2 = MockWorker("queue2", "Worker-2")
        
        assert worker1.queue_name != worker2.queue_name
        assert worker1.worker_name != worker2.worker_name
        assert worker1 is not worker2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
