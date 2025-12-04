"""
PDF extraction and text processing module with multiple fallback strategies.
"""

import logging
from pathlib import Path
from typing import Tuple, Optional
import PyPDF2
import pdfplumber

from app.utils.exceptions import PDFParsingError, InsufficientTextError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser:
    """PDF parser with multi-strategy extraction."""

    MIN_TEXT_LENGTH = 100  # Minimum characters to consider valid extraction
    MIN_TEXT_DENSITY = 0.1  # Minimum text density percentage

    @staticmethod
    def extract_pdf_text(file_path: str) -> Tuple[str, int]:
        """
        Extract text from PDF with fallback strategies.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (extracted_text, page_count)

        Raises:
            PDFParsingError: If PDF parsing fails
            InsufficientTextError: If extracted text is too short
        """
        logger.info(f"Starting PDF extraction: {file_path}")

        try:
            # Strategy 1: PyPDF2 - Fast, standard method
            text, page_count = PDFParser._extract_with_pypdf2(file_path)
            text_density = len(text) / (page_count * 5000) if page_count > 0 else 0

            if len(text) >= PDFParser.MIN_TEXT_LENGTH and text_density >= PDFParser.MIN_TEXT_DENSITY:
                logger.info(f"Successfully extracted text using PyPDF2 ({len(text)} characters)")
                return PDFParser._clean_text(text), page_count

            logger.debug("PyPDF2 extraction insufficient, trying pdfplumber...")

            # Strategy 2: pdfplumber - Better for complex layouts
            text, page_count = PDFParser._extract_with_pdfplumber(file_path)

            if len(text) >= PDFParser.MIN_TEXT_LENGTH:
                logger.info(f"Successfully extracted text using pdfplumber ({len(text)} characters)")
                return PDFParser._clean_text(text), page_count

            logger.warning("Both extraction methods returned insufficient text")
            raise InsufficientTextError(
                f"Could not extract sufficient text from PDF. "
                f"Minimum required: {PDFParser.MIN_TEXT_LENGTH} characters"
            )

        except InsufficientTextError:
            raise
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            raise PDFParsingError(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def _extract_with_pypdf2(file_path: str) -> Tuple[str, int]:
        """Extract text using PyPDF2."""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                text = ""

                for page_num, page in enumerate(reader.pages):
                    try:
                        text += page.extract_text() or ""
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {str(e)}")
                        continue

                return text, page_count
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            raise

    @staticmethod
    def _extract_with_pdfplumber(file_path: str) -> Tuple[str, int]:
        """Extract text using pdfplumber."""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {str(e)}")
                        continue

                return text, page_count
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            raise

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Strip leading/trailing whitespace
            line = line.strip()
            # Skip empty lines
            if line:
                cleaned_lines.append(line)

        # Join with single newline
        text = '\n'.join(cleaned_lines)

        # Remove multiple consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')

        # Fix common encoding issues
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        return text

    @staticmethod
    def get_page_count(file_path: str) -> int:
        """Get page count of PDF."""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            logger.error(f"Failed to get page count: {str(e)}")
            return 0


class TextProcessor:
    """Text processing utilities."""

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(text.split())

    @staticmethod
    def extract_sections(text: str) -> dict:
        """
        Extract common contract sections from text.

        Returns:
            Dictionary mapping section names to section text
        """
        sections = {
            "insurance": [],
            "liability": [],
            "payment": [],
            "indemnification": [],
            "termination": [],
            "scope": []
        }

        keywords = {
            "insurance": ["insurance", "coverage", "insured", "policy"],
            "liability": ["liability", "limit", "damages", "claims"],
            "payment": ["payment", "fee", "invoice", "compensation", "price"],
            "indemnification": ["indemnif", "hold harmless", "defend"],
            "termination": ["termination", "terminate", "end", "expiration"],
            "scope": ["scope", "services", "deliverables", "work"]
        }

        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()
            for section, keywords_list in keywords.items():
                if any(keyword in line_lower for keyword in keywords_list):
                    # Include context: current line + next few lines
                    context = '\n'.join(lines[i:min(i+5, len(lines))])
                    sections[section].append(context)

        return sections
