"""
Risk detection node for the analysis graph.
"""

import json
import logging
import re
from langchain_openai import ChatOpenAI
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def detect_risks_node(state: dict) -> dict:
    """Detect contract risks using LLM analysis."""
    logger.info("Starting risk detection...")

    try:
        clauses = state.get("extracted_clauses", [])
        if not clauses:
            logger.warning("No clauses available for risk detection")
            state["detected_risks"] = []
            return state

        # Simple clause formatting
        clauses_text = "\n".join([
            f"- {c.get('title', 'Unknown')}: {c.get('text', '')}"
            for c in clauses
        ])

        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature
        )

        # Simple prompt
        prompt = f"""Analyze these contract clauses and identify risks:

{clauses_text}

Return a JSON array with detected risks. For each risk include:
- category: one of 'missing_insurance', 'uncapped_liability', 'vague_payment_terms', 'broad_indemnification', 'missing_termination', 'ambiguous_scope'
- title: short risk title
- description: detailed description
- affected_clause: which clause
- explanation: why it's risky
- evidence: list of relevant quotes
- financial_impact: LOW, MEDIUM, or HIGH
- likelihood: LOW, MEDIUM, or HIGH

Return ONLY the JSON array, no markdown or extra text."""

        response = await llm.ainvoke(prompt)
        response_text = response.content

        # Extract JSON
        risks = _extract_json_array(response_text)
        if risks:
            # Normalize categories to lowercase
            for risk in risks:
                if "category" in risk:
                    risk["category"] = str(risk["category"]).lower().replace(" ", "_")

            state["detected_risks"] = risks
            state["current_step"] = "risk_detection_complete"
            logger.info(f"Detected {len(risks)} risks")
        else:
            logger.warning("Could not parse risks from response")
            state["detected_risks"] = []
            state["errors"].append("Failed to detect risks")

        return state

    except Exception as e:
        logger.error(f"Risk detection error: {str(e)}")
        state["errors"].append(f"Risk detection error: {str(e)}")
        state["current_step"] = "risk_detection_failed"
        state["detected_risks"] = []
        return state


def _extract_json_array(text: str) -> list | None:
    """Extract JSON array from text."""
    # Try code block first
    match = re.search(r'```(?:json)?\s*\n([\s\S]*?)\n```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find [ ] brackets
    try:
        start = text.find('[')
        if start != -1:
            end = text.rfind(']')
            if end > start:
                return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        pass

    return None
