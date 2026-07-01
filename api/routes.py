"""FastAPI routes for loan approval microservice"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.config import settings
from src.models.schemas import (
    LoanApplication,
    FinalDecision,
    ApplicationStatus,
    DecisionStatus
)
from src.orchestrator import LoanApprovalOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["loan-approval"])

# Initialize orchestrator singleton
orchestrator = LoanApprovalOrchestrator()

# In-memory application storage (replace with database in production)
application_store: Dict[str, Dict[str, Any]] = {}


@router.post("/apply", response_model=dict)
async def submit_loan_application(application: LoanApplication):
    """
    Submit a new loan application for processing

    Args:
        application: Loan application data

    Returns:
        Application submission acknowledgment with case ID
    """
    try:
        logger.info(f"Received loan application from {application.applicant_id}")

        # Convert to dict for processing
        app_data = application.model_dump()

        # Store application
        app_record = {
            "applicant_id": application.applicant_id,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "application_data": app_data,
            "final_decision": None
        }
        application_store[application.applicant_id] = app_record

        # Process application asynchronously
        asyncio.create_task(
            process_application_async(application.applicant_id, app_data)
        )

        return {
            "status": "accepted",
            "applicant_id": application.applicant_id,
            "message": "Application received and queued for processing",
            "created_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{applicant_id}", response_model=ApplicationStatus)
async def get_application_status(applicant_id: str):
    """
    Get current status of a loan application

    Args:
        applicant_id: Applicant identifier

    Returns:
        Current application status and decision (if available)
    """
    try:
        if applicant_id not in application_store:
            raise HTTPException(status_code=404, detail=f"Application {applicant_id} not found")

        app_record = application_store[applicant_id]

        response = ApplicationStatus(
            applicant_id=applicant_id,
            status=DecisionStatus(app_record.get("status", "processing")),
            risk_score=app_record.get("risk_score", 0),
            created_at=datetime.fromisoformat(app_record.get("created_at")),
            updated_at=datetime.fromisoformat(app_record.get("updated_at")),
            final_decision=app_record.get("final_decision")
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching application status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/decision/{applicant_id}")
async def get_loan_decision(applicant_id: str):
    """
    Get final loan decision for an application

    Args:
        applicant_id: Applicant identifier

    Returns:
        Complete loan decision with explanations
    """
    try:
        if applicant_id not in application_store:
            raise HTTPException(status_code=404, detail=f"Application {applicant_id} not found")

        app_record = application_store[applicant_id]

        if app_record.get("status") == "processing":
            raise HTTPException(status_code=202, detail="Application still processing")

        if not app_record.get("final_decision"):
            raise HTTPException(status_code=404, detail="Decision not yet available")

        return {
            "applicant_id": applicant_id,
            "decision": app_record.get("final_decision")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching decision: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        System health status
    """
    try:
        health_status = await orchestrator.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/metrics")
async def get_metrics():
    """
    Get execution metrics

    Returns:
        System metrics and statistics
    """
    try:
        metrics = orchestrator.get_execution_metrics()
        metrics["total_applications"] = len(application_store)
        metrics["timestamp"] = datetime.utcnow().isoformat()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/applications")
async def list_applications():
    """
    List all applications (admin endpoint)

    Returns:
        List of all applications with their status
    """
    try:
        applications = []
        for app_id, app_data in application_store.items():
            applications.append({
                "applicant_id": app_id,
                "status": app_data.get("status"),
                "created_at": app_data.get("created_at"),
                "updated_at": app_data.get("updated_at")
            })
        return {
            "total": len(applications),
            "applications": applications
        }
    except Exception as e:
        logger.error(f"Error listing applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_application_async(applicant_id: str, application_data: Dict[str, Any]):
    """
    Background task to process loan application
    """
    try:
        logger.info(f"Processing application for {applicant_id}")

        # Process through orchestrator
        result = await orchestrator.process_loan_application(application_data)

        # Update application store
        app_record = application_store[applicant_id]
        app_record["status"] = result.get("application_status", "completed")
        app_record["risk_score"] = result.get("risk_score", 0)
        app_record["final_decision"] = result
        app_record["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"Application processing completed for {applicant_id}: {app_record['status']}")

    except Exception as e:
        logger.error(f"Error processing application {applicant_id}: {str(e)}")
        if applicant_id in application_store:
            application_store[applicant_id]["status"] = "failed"
            application_store[applicant_id]["error"] = str(e)
            application_store[applicant_id]["updated_at"] = datetime.utcnow().isoformat()
