"""
LangGraph state machine for contract risk analysis agent.
"""

import logging
import uuid
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.utils.logger import setup_logger
from app.agents.state import ContractAnalysisState
from app.agents.nodes.extraction import extract_clauses_node
from app.agents.nodes.risk_detection import detect_risks_node
from app.agents.nodes.scoring import score_risks_node
from app.agents.nodes.remediation import generate_remediation_node

logger = setup_logger(__name__)


def create_analysis_graph():
    """Create the contract analysis workflow graph."""

    # Initialize graph
    workflow = StateGraph(ContractAnalysisState)

    # Add nodes
    workflow.add_node("parse", parse_node)
    workflow.add_node("extract", extract_clauses_node)
    workflow.add_node("detect_risks", detect_risks_node)
    workflow.add_node("score_risks", score_risks_node)
    workflow.add_node("remediation", generate_remediation_node)

    # Add edges
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "extract")
    workflow.add_edge("extract", "detect_risks")
    workflow.add_edge("detect_risks", "score_risks")
    workflow.add_edge("score_risks", "remediation")
    workflow.add_edge("remediation", END)

    # Compile graph
    return workflow.compile()


async def parse_node(state: dict) -> dict:
    """Initial parsing node - validates input state."""
    logger.info(f"Starting analysis for {state.get('contract_filename', 'unknown')}")

    try:
        # Validate required fields
        if not state.get("contract_text"):
            state["errors"] = ["No contract text provided"]
            state["current_step"] = "parse_failed"
            return state

        # Initialize fields if not present
        if "analysis_id" not in state:
            state["analysis_id"] = str(uuid.uuid4())

        if "errors" not in state:
            state["errors"] = []

        if "extracted_clauses" not in state:
            state["extracted_clauses"] = []

        if "detected_risks" not in state:
            state["detected_risks"] = []

        if "scored_risks" not in state:
            state["scored_risks"] = []

        if "remediation_suggestions" not in state:
            state["remediation_suggestions"] = []

        if "overall_risk_score" not in state:
            state["overall_risk_score"] = 0

        if "summary" not in state:
            state["summary"] = ""

        if "is_complete" not in state:
            state["is_complete"] = False

        if "current_step" not in state:
            state["current_step"] = "parsing"

        logger.info(f"Analysis {state['analysis_id']} initialized")
        state["current_step"] = "parse_complete"
        return state

    except Exception as e:
        logger.error(f"Parse node error: {str(e)}")
        state["errors"].append(f"Parse error: {str(e)}")
        state["current_step"] = "parse_failed"
        return state


class AnalysisExecutor:
    """Execute contract analysis using the compiled graph."""

    def __init__(self):
        """Initialize the analysis executor."""
        self.graph = create_analysis_graph()

    async def analyze(self, contract_text: str, filename: str = "contract.pdf") -> dict:
        """
        Execute analysis on contract text.

        Args:
            contract_text: The extracted contract text
            filename: Original filename

        Returns:
            Analysis results dictionary
        """
        logger.info(f"Starting analysis execution for {filename}")

        # Count words
        word_count = len(contract_text.split())

        # Initialize state
        initial_state: ContractAnalysisState = {
            "contract_text": contract_text,
            "contract_filename": filename,
            "page_count": 0,
            "word_count": word_count,
            "extracted_clauses": [],
            "detected_risks": [],
            "scored_risks": [],
            "remediation_suggestions": [],
            "analysis_id": str(uuid.uuid4()),
            "overall_risk_score": 0,
            "summary": "",
            "current_step": "initialized",
            "errors": [],
            "is_complete": False
        }

        try:
            # Invoke graph
            result = await self.graph.ainvoke(initial_state)

            # Generate summary
            if result.get("scored_risks"):
                risk_count = len(result["scored_risks"])
                critical = sum(1 for r in result["scored_risks"] if r.get("severity_level") == "CRITICAL")
                high = sum(1 for r in result["scored_risks"] if r.get("severity_level") == "HIGH")

                summary = (
                    f"Analysis complete. Found {risk_count} risks: "
                    f"{critical} critical, {high} high. "
                    f"Overall risk score: {result.get('overall_risk_score', 0)}/100"
                )
                result["summary"] = summary
            else:
                result["summary"] = "No significant risks detected in contract."

            logger.info(f"Analysis {result['analysis_id']} completed")
            return result

        except Exception as e:
            logger.error(f"Analysis execution error: {str(e)}", exc_info=True)
            return {
                "analysis_id": initial_state["analysis_id"],
                "contract_filename": filename,
                "current_step": "execution_failed",
                "errors": [str(e)],
                "is_complete": False,
                "scored_risks": [],
                "overall_risk_score": 0,
                "summary": f"Analysis failed: {str(e)}"
            }
