"""Resize Worker"""

from app.shared.base.worker import BaseWorker
from app.modules.resize.service import ResizeService
from app.core.config import RABBITMQ_CONFIG
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


class ResizeWorker(BaseWorker):
    """Worker for image resizing"""
    
    def __init__(self):
        super().__init__(
            queue_name=RABBITMQ_CONFIG.RESIZE_QUEUE,
            worker_name="ResizeWorker"
        )
        self.service = ResizeService()
    
    def process(self, message: dict) -> dict:
        """Process resize task"""
        return self.service.execute(message)


if __name__ == "__main__":
    worker = ResizeWorker()
    worker.start_consuming()
