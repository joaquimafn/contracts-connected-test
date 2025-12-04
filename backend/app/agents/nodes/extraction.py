"""
Clause extraction node for the analysis graph.
"""

import json
import logging
from typing import Any
from langchain_openai import ChatOpenAI
from app.config import settings
from app.utils.logger import setup_logger
from app.agents.prompts.extraction_prompts import EXTRACT_CLAUSES_PROMPT

logger = setup_logger(__name__)


async def extract_clauses_node(state: dict) -> dict:
    """Extract key clauses from contract using LLM."""
    logger.info("Starting clause extraction...")

    try:
        contract_text = state.get("contract_text", "")
        if not contract_text:
            state["errors"].append("No contract text available for extraction")
            return state

        # Initialize LLM
        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature
        )

        # Format prompt
        prompt = EXTRACT_CLAUSES_PROMPT.format(contract_text=contract_text)

        # Call LLM
        response = await llm.ainvoke(prompt)
        response_text = response.content

        # Parse JSON response with robust extraction
        try:
            clauses = _parse_json_response(response_text, logger)

            if clauses is None:
                logger.warning("Could not parse clauses from LLM response, using fallback")
                state["extracted_clauses"] = [{"text": response_text, "section": "full_text"}]
            else:
                state["extracted_clauses"] = clauses
                state["current_step"] = "extraction_complete"
                logger.info(f"Successfully extracted {len(clauses)} clauses")

        except Exception as json_err:
            logger.warning(f"JSON parsing error in extraction: {str(json_err)}")
            state["extracted_clauses"] = [{"text": response_text, "section": "full_text"}]

        return state

    except Exception as e:
        logger.error(f"Clause extraction error: {str(e)}", exc_info=True)
        state["errors"].append(f"Extraction error: {str(e)}")
        state["current_step"] = "extraction_failed"
        return state


def _parse_json_response(response_text: str, logger) -> list | None:
    """
    Robustly extract JSON array from LLM response.

    Handles responses with markdown, extra text, etc.
    """
    import re

    # Strategy 1: Look for ```json...``` code block
    json_block = re.search(r'```(?:json)?\s*\n([\s\S]*?)\n```', response_text)
    if json_block:
        try:
            return json.loads(json_block.group(1))
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse JSON from code block: {e}")

    # Strategy 2: Look for [...] pattern (more conservative)
    # This uses a different approach - find first [ and match brackets
    try:
        start_idx = response_text.find('[')
        if start_idx != -1:
            # Try to find matching closing bracket
            bracket_count = 0
            end_idx = -1
            for i in range(start_idx, len(response_text)):
                if response_text[i] == '[':
                    bracket_count += 1
                elif response_text[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break

            if end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.debug(f"Failed to parse bracketed JSON: {e}")

    # Strategy 3: Try direct JSON parsing (last resort)
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.debug(f"Failed direct JSON parse: {e}")

    # All strategies failed
    logger.error(f"Could not extract JSON from response. First 200 chars: {response_text[:200]}")
    return None
