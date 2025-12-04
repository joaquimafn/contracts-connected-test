"""
Custom exception classes for contract analysis.
"""


class ContractAnalysisError(Exception):
    """Base exception for contract analysis operations."""
    pass


class PDFParsingError(ContractAnalysisError):
    """Exception raised when PDF parsing fails."""
    pass


class InsufficientTextError(ContractAnalysisError):
    """Exception raised when extracted text is insufficient for analysis."""
    pass


class LLMError(ContractAnalysisError):
    """Exception raised when LLM API fails."""
    pass


class ValidationError(ContractAnalysisError):
    """Exception raised when input validation fails."""
    pass


class FileProcessingError(ContractAnalysisError):
    """Exception raised when file processing fails."""
    pass
