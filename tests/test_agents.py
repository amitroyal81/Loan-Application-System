"""Unit tests for agents"""

import pytest
import asyncio
from src.agents import (
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceActionAgent
)


@pytest.fixture
def sample_application():
    """Sample loan application for testing"""
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
async def test_applicant_profile_agent(sample_application):
    """Test applicant profile agent"""
    agent = ApplicantProfileAgent()
    result = await agent.execute(sample_application)

    assert result is not None
    assert "applicant_id" in result
    assert "income_stability_score" in result
    assert "employment_risk" in result
    assert "credit_history_summary" in result
    assert result["applicant_id"] == "TEST001"


@pytest.mark.asyncio
async def test_financial_risk_agent(sample_application):
    """Test financial risk agent"""
    agent = FinancialRiskAgent()
    result = await agent.execute(sample_application)

    assert result is not None
    assert "debt_to_income_ratio" in result
    assert "credit_score_risk_level" in result
    assert "risk_score" in result
    assert result["risk_score"] >= 0 and result["risk_score"] <= 100


@pytest.mark.asyncio
async def test_decision_agent(sample_application):
    """Test decision agent"""
    # First get outputs from other agents
    applicant_agent = ApplicantProfileAgent()
    risk_agent = FinancialRiskAgent()

    applicant_output = await applicant_agent.execute(sample_application)
    risk_output = await risk_agent.execute(sample_application)

    # Now test decision agent
    decision_agent = LoanDecisionAgent()
    decision_input = {
        "applicant_id": sample_application["applicant_id"],
        "applicant_profile": applicant_output,
        "financial_risk": risk_output,
        "application_data": sample_application
    }

    result = await decision_agent.execute(decision_input)

    assert result is not None
    assert "classification" in result
    assert result["classification"] in ["approved", "rejected", "manual_review"]
    assert "confidence_level" in result
    assert result["confidence_level"] >= 0 and result["confidence_level"] <= 100


@pytest.mark.asyncio
async def test_compliance_agent(sample_application):
    """Test compliance agent"""
    agent = ComplianceActionAgent()
    compliance_input = {
        "applicant_id": sample_application["applicant_id"],
        "decision": "approved",
        "risk_score": 35,
        "applicant_name": sample_application["applicant_name"]
    }

    result = await agent.execute(compliance_input)

    assert result is not None
    assert "case_id" in result
    assert "action_taken" in result
    assert "notification_sent" in result
    assert result["notification_sent"] is True
