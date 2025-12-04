"""
Remediation suggestion node for the analysis graph.
"""

import json
import logging
from langchain_openai import ChatOpenAI
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def generate_remediation_node(state: dict) -> dict:
    """Generate remediation suggestions for identified risks."""
    logger.info("Starting remediation generation...")

    try:
        risks = state.get("scored_risks", [])
        if not risks:
            state["remediation_suggestions"] = []
            return state

        remediation_suggestions = []

        for risk in risks:
            try:
                # Default remediation
                suggestion = f"Review and negotiate the {risk.get('title', 'risk')} with legal counsel."

                risk["remediation"] = {
                    "suggestion": suggestion,
                    "priority": risk.get("severity_level", "MEDIUM"),
                    "effort": "MEDIUM"
                }
                remediation_suggestions.append(risk["remediation"])

            except Exception as e:
                logger.warning(f"Error generating remediation: {str(e)}")
                risk["remediation"] = {
                    "suggestion": "Review and negotiate this clause",
                    "priority": risk.get("severity_level", "MEDIUM"),
                    "effort": "MEDIUM"
                }
                remediation_suggestions.append(risk["remediation"])

        state["remediation_suggestions"] = remediation_suggestions
        state["current_step"] = "remediation_complete"
        state["is_complete"] = True

        logger.info("Remediation generation complete")
        return state

    except Exception as e:
        logger.error(f"Remediation generation error: {str(e)}")
        state["errors"].append(f"Remediation error: {str(e)}")
        state["current_step"] = "remediation_failed"
        return state
