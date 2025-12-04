"""
Pydantic models for risk data structures.
"""

from typing import List
from enum import Enum
from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    """Risk categories enumeration."""
    MISSING_INSURANCE = "missing_insurance"
    UNCAPPED_LIABILITY = "uncapped_liability"
    VAGUE_PAYMENT_TERMS = "vague_payment_terms"
    BROAD_INDEMNIFICATION = "broad_indemnification"
    MISSING_TERMINATION = "missing_termination"
    AMBIGUOUS_SCOPE = "ambiguous_scope"


class SeverityLevel(str, Enum):
    """Severity levels for risks."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RemediationModel(BaseModel):
    """Remediation suggestion model."""
    suggestion: str = Field(..., description="Suggested remediation action")
    priority: str = Field(..., description="Priority level")
    effort: str = Field(..., description="Implementation effort level")


class RiskModel(BaseModel):
    """Individual risk model."""
    risk_id: str = Field(..., description="Unique risk identifier")
    category: RiskCategory = Field(..., description="Risk category")
    title: str = Field(..., description="Brief risk title")
    description: str = Field(..., description="Detailed risk description")
    severity_score: int = Field(..., ge=0, le=100, description="Severity score 0-100")
    severity_level: SeverityLevel = Field(..., description="Severity level")
    affected_clause: str = Field(..., description="Affected contract clause")
    explanation: str = Field(..., description="Why this is problematic")
    evidence: List[str] = Field(default_factory=list, description="Evidence quotes")
    remediation: RemediationModel = Field(..., description="Remediation suggestion")


class ContractMetadata(BaseModel):
    """Contract metadata model."""
    filename: str
    file_type: str
    page_count: int = 0
    word_count: int = 0


class AnalysisResultModel(BaseModel):
    """Complete analysis result model."""
    analysis_id: str
    status: str = "completed"
    contract_metadata: ContractMetadata
    risks: List[RiskModel]
    overall_risk_score: int = Field(..., ge=0, le=100)
    summary: str
    analyzed_at: str
