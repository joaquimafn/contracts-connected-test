"""
Pydantic models for contract operations.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AnalysisStatusResponse(BaseModel):
    """Response model for analysis status."""
    analysis_id: str
    status: str = Field(..., description="Status: pending, processing, completed, failed")
    progress_percentage: int = Field(default=0, ge=0, le=100)
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class UploadResponse(BaseModel):
    """Response model for file upload."""
    analysis_id: str
    status: str = "pending"
    created_at: str
    message: str = "Contract received and queued for analysis"
