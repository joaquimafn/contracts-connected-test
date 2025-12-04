"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Contract Risk Analysis Agent API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
