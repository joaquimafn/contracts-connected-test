"""
Contract analysis endpoints.
"""

import json
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.utils.logger import setup_logger
from app.utils.exceptions import ValidationError, FileProcessingError, ContractAnalysisError
from app.core.file_handler import FileHandler
from app.core.pdf_parser import PDFParser
from app.agents.graph import AnalysisExecutor
from app.api.schemas.contract import UploadResponse, AnalysisStatusResponse
from app.api.schemas.risk import AnalysisResultModel, ContractMetadata, RiskModel, RemediationModel

logger = setup_logger(__name__)

# In-memory storage for analysis results (for demo purposes)
# In production, use a database
ANALYSIS_STORAGE = {}
ANALYSIS_EXECUTOR = AnalysisExecutor()

router = APIRouter(prefix="/api/v1", tags=["contracts"])


@router.post("/contracts/upload", response_model=UploadResponse, status_code=202)
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a contract for analysis.

    Accepts PDF or TXT files (max 10MB).
    Returns analysis ID for polling results.
    """
    analysis_id = None

    try:
        # Validate file
        FileHandler.validate_file(file)

        # Save file temporarily
        file_path = await FileHandler.save_temp_file(file)

        # Extract text based on file type
        if file.filename.lower().endswith(".pdf"):
            contract_text, page_count = PDFParser.extract_pdf_text(file_path)
        else:  # .txt
            contract_text = FileHandler.read_text_file(file_path)
            page_count = 0

        # Validate extracted text
        if not contract_text or len(contract_text) < 100:
            raise ValidationError("Could not extract sufficient text from file")

        # Create analysis record
        analysis_id = file.filename.replace(".", "_") + "_" + str(datetime.utcnow().timestamp()).replace(".", "")[:10]

        ANALYSIS_STORAGE[analysis_id] = {
            "status": "pending",
            "filename": file.filename,
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "result": None,
            "error": None
        }

        # Queue analysis (in production, use Celery/RQ)
        import asyncio
        asyncio.create_task(_run_analysis(analysis_id, contract_text, file.filename, file_path))

        logger.info(f"File uploaded: {file.filename} -> Analysis ID: {analysis_id}")

        return UploadResponse(
            analysis_id=analysis_id,
            status="pending",
            created_at=ANALYSIS_STORAGE[analysis_id]["created_at"]
        )

    except ValidationError as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileProcessingError as e:
        logger.error(f"File processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during upload")


@router.get("/contracts/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis."""
    if analysis_id not in ANALYSIS_STORAGE:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = ANALYSIS_STORAGE[analysis_id]

    return AnalysisStatusResponse(
        analysis_id=analysis_id,
        status=analysis["status"],
        progress_percentage=analysis.get("progress", 0),
        created_at=analysis.get("created_at"),
        completed_at=analysis.get("completed_at"),
        error_message=analysis.get("error")
    )


@router.get("/contracts/{analysis_id}/results")
async def get_analysis_results(analysis_id: str):
    """Get the results of a completed analysis."""
    if analysis_id not in ANALYSIS_STORAGE:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = ANALYSIS_STORAGE[analysis_id]

    if analysis["status"] == "pending" or analysis["status"] == "processing":
        raise HTTPException(status_code=202, detail="Analysis still processing")

    if analysis["status"] == "failed":
        raise HTTPException(status_code=400, detail=analysis.get("error", "Analysis failed"))

    return analysis.get("result")


async def _run_analysis(analysis_id: str, contract_text: str, filename: str, file_path: str):
    """Run analysis in background."""
    try:
        ANALYSIS_STORAGE[analysis_id]["status"] = "processing"
        ANALYSIS_STORAGE[analysis_id]["progress"] = 10

        logger.info(f"Starting analysis: {analysis_id}")

        # Run analysis
        result = await ANALYSIS_EXECUTOR.analyze(contract_text, filename)

        # Format result for response
        metadata = ContractMetadata(
            filename=filename,
            file_type="pdf" if filename.endswith(".pdf") else "txt",
            page_count=result.get("page_count", 0),
            word_count=result.get("word_count", 0)
        )

        # Format risks
        risks = []
        for risk in result.get("scored_risks", []):
            remediation = RemediationModel(
                suggestion=risk.get("remediation", {}).get("suggestion", ""),
                priority=risk.get("remediation", {}).get("priority", "MEDIUM"),
                effort=risk.get("remediation", {}).get("effort", "MEDIUM")
            )

            risk_model = RiskModel(
                risk_id=risk.get("risk_id", ""),
                category=risk.get("category", ""),
                title=risk.get("title", ""),
                description=risk.get("description", ""),
                severity_score=risk.get("severity_score", 50),
                severity_level=risk.get("severity_level", "MEDIUM"),
                affected_clause=risk.get("affected_clause", ""),
                explanation=risk.get("explanation", ""),
                evidence=risk.get("evidence", []),
                remediation=remediation
            )
            risks.append(risk_model)

        formatted_result = {
            "analysis_id": result.get("analysis_id", analysis_id),
            "status": "completed",
            "contract_metadata": metadata.dict(),
            "risks": [r.dict() for r in risks],
            "overall_risk_score": result.get("overall_risk_score", 0),
            "summary": result.get("summary", ""),
            "analyzed_at": datetime.utcnow().isoformat()
        }

        ANALYSIS_STORAGE[analysis_id]["result"] = formatted_result
        ANALYSIS_STORAGE[analysis_id]["status"] = "completed"
        ANALYSIS_STORAGE[analysis_id]["completed_at"] = datetime.utcnow().isoformat()
        ANALYSIS_STORAGE[analysis_id]["progress"] = 100

        logger.info(f"Analysis completed: {analysis_id}")

    except Exception as e:
        logger.error(f"Analysis execution error: {str(e)}", exc_info=True)
        ANALYSIS_STORAGE[analysis_id]["status"] = "failed"
        ANALYSIS_STORAGE[analysis_id]["error"] = str(e)
        ANALYSIS_STORAGE[analysis_id]["progress"] = 0

    finally:
        # Cleanup temp file
        try:
            FileHandler.cleanup_temp_file(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {str(e)}")
