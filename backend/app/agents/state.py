"""
State definitions for the contract analysis agent.
"""

from typing import TypedDict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Clause:
    """Represents an extracted contract clause."""
    section: str
    title: str
    text: str
    page_reference: Optional[int] = None


@dataclass
class Risk:
    """Represents an identified risk."""
    risk_id: str
    category: str
    title: str
    description: str
    severity_score: int
    severity_level: str
    affected_clause: str
    explanation: str
    evidence: List[str] = field(default_factory=list)
    financial_impact: str = "MEDIUM"
    likelihood: str = "MEDIUM"
    remediation_suggestion: Optional[str] = None
    remediation_priority: Optional[str] = None
    remediation_effort: Optional[str] = None


class ContractAnalysisState(TypedDict):
    """State dictionary for the contract analysis graph."""
    # Input
    contract_text: str
    contract_filename: str
    page_count: int
    word_count: int

    # Processing stages
    extracted_clauses: List[dict]  # List of extracted clauses
    detected_risks: List[dict]     # Raw risks from LLM
    scored_risks: List[dict]       # Scored and formatted risks
    remediation_suggestions: List[dict]  # Remediation for each risk

    # Metadata
    analysis_id: str
    overall_risk_score: int
    summary: str
    current_step: str
    errors: List[str]
    is_complete: bool
