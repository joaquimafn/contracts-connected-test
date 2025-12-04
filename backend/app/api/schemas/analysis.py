"""
Analysis response models.
"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    request_id: str = ""
