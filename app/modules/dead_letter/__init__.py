"""Initialize Dead Letter module"""
from app.modules.dead_letter.worker import DeadLetterWorker, DeadLetterService

__all__ = ["DeadLetterWorker", "DeadLetterService"]
