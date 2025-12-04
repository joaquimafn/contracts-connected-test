"""
File upload and validation utilities.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from app.config import settings
from app.utils.logger import setup_logger
from app.utils.exceptions import ValidationError, FileProcessingError

logger = setup_logger(__name__)


class FileHandler:
    """Handle file uploads and validation."""

    ALLOWED_EXTENSIONS = {"pdf", "txt"}

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate uploaded file."""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        allowed = settings.get_allowed_file_types()
        if file_ext not in allowed:
            raise ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed)}"
            )

        # Check file size (max 10MB by default)
        max_size = settings.max_file_size_mb * 1024 * 1024
        if file.size and file.size > max_size:
            raise ValidationError(
                f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )

        logger.info(f"File validation passed: {file.filename}")

    @staticmethod
    async def save_temp_file(file: UploadFile) -> str:
        """
        Save uploaded file to temporary directory.

        Args:
            file: Uploaded file

        Returns:
            Path to saved file
        """
        try:
            FileHandler.validate_file(file)

            # Create temp directory if not exists
            temp_dir = Path(tempfile.gettempdir()) / "contract_analysis"
            temp_dir.mkdir(exist_ok=True)

            # Save file
            file_path = temp_dir / file.filename
            content = await file.read()

            with open(file_path, 'wb') as f:
                f.write(content)

            logger.info(f"File saved: {file_path}")
            return str(file_path)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise FileProcessingError(f"Failed to process file: {str(e)}")

    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")

    @staticmethod
    def read_text_file(file_path: str) -> str:
        """Read text from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            raise FileProcessingError(f"Failed to read text file: {str(e)}")
