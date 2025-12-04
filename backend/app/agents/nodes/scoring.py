"""
Risk severity scoring node for the analysis graph.
"""

import json
import logging
import uuid
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


SEVERITY_SCORE_RANGES = {
    "LOW": (0, 25),
    "MEDIUM": (26, 50),
    "HIGH": (51, 75),
    "CRITICAL": (76, 100)
}


def get_severity_level(score: int) -> str:
    """Get severity level from score."""
    for level, (min_val, max_val) in SEVERITY_SCORE_RANGES.items():
        if min_val <= score <= max_val:
            return level
    return "CRITICAL" if score > 100 else "LOW"


async def score_risks_node(state: dict) -> dict:
    """Score detected risks for severity."""
    logger.info("Starting risk scoring...")

    try:
        risks = state.get("detected_risks", [])
        if not risks:
            state["scored_risks"] = []
            state["overall_risk_score"] = 0
            state["current_step"] = "scoring_complete"
            return state

        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature
        )

        scored_risks = []
        total_score = 0

        for risk in risks:
            try:
                # Simple scoring
                score = _calculate_score(risk)

                # Build scored risk
                scored_risk = {
                    "risk_id": str(uuid.uuid4()),
                    "category": risk.get("category", ""),
                    "title": risk.get("title", ""),
                    "description": risk.get("description", ""),
                    "severity_score": score,
                    "severity_level": get_severity_level(score),
                    "affected_clause": risk.get("affected_clause", ""),
                    "explanation": risk.get("explanation", ""),
                    "evidence": risk.get("evidence", []),
                    "remediation": {
                        "suggestion": "",
                        "priority": "MEDIUM",
                        "effort": "MEDIUM"
                    }
                }

                scored_risks.append(scored_risk)
                total_score += score

            except Exception as e:
                logger.warning(f"Error scoring risk: {str(e)}")
                scored_risks.append({
                    "risk_id": str(uuid.uuid4()),
                    "category": risk.get("category", ""),
                    "title": risk.get("title", "Unknown Risk"),
                    "description": risk.get("description", ""),
                    "severity_score": 50,
                    "severity_level": "MEDIUM",
                    "affected_clause": risk.get("affected_clause", ""),
                    "explanation": risk.get("explanation", ""),
                    "evidence": risk.get("evidence", []),
                    "remediation": {
                        "suggestion": "",
                        "priority": "MEDIUM",
                        "effort": "MEDIUM"
                    }
                })
                total_score += 50

        # Calculate overall risk score
        overall_risk_score = int(total_score / len(scored_risks)) if scored_risks else 0
        overall_risk_score = max(0, min(100, overall_risk_score))

        state["scored_risks"] = scored_risks
        state["overall_risk_score"] = overall_risk_score
        state["current_step"] = "scoring_complete"

        logger.info(f"Scored {len(scored_risks)} risks. Overall: {overall_risk_score}")
        return state

    except Exception as e:
        logger.error(f"Scoring error: {str(e)}")
        state["errors"].append(f"Scoring error: {str(e)}")
        state["current_step"] = "scoring_failed"
        return state


def _calculate_score(risk: dict) -> int:
    """Calculate risk score from impact and likelihood."""
    impact_scores = {
        "LOW": 35,
        "MEDIUM": 60,
        "HIGH": 80
    }

    likelihood_multipliers = {
        "LOW": 0.7,
        "MEDIUM": 1.0,
        "HIGH": 1.3
    }

    base = impact_scores.get(risk.get("financial_impact", "MEDIUM"), 50)
    mult = likelihood_multipliers.get(risk.get("likelihood", "MEDIUM"), 1.0)

    score = int(base * mult)
    return max(0, min(100, score))
