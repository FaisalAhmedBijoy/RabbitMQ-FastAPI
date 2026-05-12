"""Resize Consumer"""

from app.modules.resize.worker import ResizeWorker


def start_resize_consumer():
    """Start resize consumer"""
    worker = ResizeWorker()
    worker.start_consuming()
