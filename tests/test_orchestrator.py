"""Tests for orchestrator"""

import pytest
from src.orchestrator import LoanApprovalOrchestrator


@pytest.fixture
def orchestrator():
    """Create orchestrator instance"""
    return LoanApprovalOrchestrator()


@pytest.fixture
def sample_application():
    """Sample loan application"""
    return {
        "applicant_id": "TEST001",
        "applicant_name": "Test User",
        "age": 35,
        "income": 5000,
        "employment_type": "salaried",
        "credit_score": 720,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "existing_liabilities": 10000,
        "location": "California",
        "employment_years": 5
    }


@pytest.mark.asyncio
async def test_orchestrator_process_application(orchestrator, sample_application):
    """Test complete orchestration workflow"""
    result = await orchestrator.process_loan_application(sample_application)

    assert result is not None
    assert "applicant_id" in result
    assert "application_status" in result
    assert result["application_status"] in ["approved", "rejected", "manual_review"]
    assert "risk_score" in result
    assert "case_id" in result
    assert "processing_duration_seconds" in result


@pytest.mark.asyncio
async def test_orchestrator_health_check(orchestrator):
    """Test orchestrator health check"""
    health = await orchestrator.health_check()

    assert health is not None
    assert health.get("status") == "healthy"
    assert "orchestrator_state" in health
    assert "agents_initialized" in health
