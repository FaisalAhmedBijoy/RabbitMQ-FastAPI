"""
Worker Launcher
Central management for all workers
"""

import sys
from multiprocessing import Process
from app.shared.helpers.logger import setup_logger

logger = setup_logger(__name__)


def start_resize_worker():
    """Start resize worker"""
    from app.modules.resize.worker import ResizeWorker
    worker = ResizeWorker()
    worker.start_consuming()


def start_thumbnail_worker():
    """Start thumbnail worker"""
    from app.modules.thumbnail.worker import ThumbnailWorker
    worker = ThumbnailWorker()
    worker.start_consuming()


def start_ocr_worker():
    """Start OCR worker"""
    from app.modules.ocr.worker import OCRWorker
    worker = OCRWorker()
    worker.start_consuming()


def start_ai_tagging_worker():
    """Start AI tagging worker"""
    from app.modules.ai_tagging.worker import AITaggingWorker
    worker = AITaggingWorker()
    worker.start_consuming()


def start_retry_worker():
    """Start retry worker"""
    from app.modules.retry.worker import RetryWorker
    worker = RetryWorker()
    worker.start_consuming()


def start_dlq_worker():
    """Start dead letter queue worker"""
    from app.modules.dead_letter.worker import DeadLetterWorker
    worker = DeadLetterWorker()
    worker.start_consuming()


def start_logging_worker():
    """Start logging worker"""
    from app.modules.logging_system.worker import LoggingWorker
    worker = LoggingWorker()
    worker.start_consuming()


def start_all_workers():
    """Start all workers in separate processes"""
    workers = [
        ("ResizeWorker", start_resize_worker),
        ("ThumbnailWorker", start_thumbnail_worker),
        ("OCRWorker", start_ocr_worker),
        ("AITaggingWorker", start_ai_tagging_worker),
        ("RetryWorker", start_retry_worker),
        ("DLQWorker", start_dlq_worker),
        ("LoggingWorker", start_logging_worker),
    ]
    
    processes = []
    
    try:
        logger.info("Starting all workers...")
        
        for name, worker_func in workers:
            p = Process(target=worker_func, name=name)
            p.start()
            processes.append(p)
            logger.info(f"{name} started (PID: {p.pid})")
        
        # Wait for all processes
        for p in processes:
            p.join()
    
    except KeyboardInterrupt:
        logger.info("Stopping all workers...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
        logger.info("All workers stopped")
    
    except Exception as e:
        logger.error(f"Error in worker launcher: {str(e)}")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
        sys.exit(1)


if __name__ == "__main__":
    start_all_workers()
