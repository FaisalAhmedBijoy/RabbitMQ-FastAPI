"""
Monitoring Routes
Application health and monitoring endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["monitoring"])


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Async Image Processing Pipeline"}


@router.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )
