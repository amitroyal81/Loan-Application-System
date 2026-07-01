"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    FREELANCE = "freelance"
    UNEMPLOYED = "unemployed"


class DecisionStatus(str, Enum):
    """Loan decision status"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class LoanApplication(BaseModel):
    """Loan application input data"""
    applicant_id: str = Field(..., description="Unique applicant identifier")
    applicant_name: str = Field(..., description="Full name of applicant")
    age: int = Field(..., ge=18, le=120, description="Age of applicant")
    income: float = Field(..., gt=0, description="Monthly income in currency units")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_tenure_months: int = Field(..., gt=0, description="Loan tenure in months")
    existing_liabilities: float = Field(default=0, ge=0, description="Existing debts/liabilities")
    location: str = Field(..., description="Applicant location/state")
    employment_years: float = Field(..., ge=0, description="Years of employment")

    class Config:
        json_schema_extra = {
            "example": {
                "applicant_id": "APP001",
                "applicant_name": "John Doe",
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
        }


class ApplicantProfileOutput(BaseModel):
    """Output from Applicant Profile Agent"""
    income_stability_score: float = Field(..., ge=0, le=100)
    employment_risk: str = Field(..., description="low/medium/high")
    credit_history_summary: str = Field(...)
    application_completeness: float = Field(..., ge=0, le=100)
    flags: List[str] = Field(default_factory=list)
    reasoning: str = Field(...)


class FinancialRiskOutput(BaseModel):
    """Output from Financial Risk Analysis Agent"""
    debt_to_income_ratio: float = Field(...)
    credit_score_risk_level: str = Field(..., description="low/medium/high")
    loan_amount_risk: str = Field(..., description="low/medium/high")
    anomaly_detected: bool = Field(...)
    anomaly_details: Optional[str] = Field(default=None)
    risk_score: float = Field(..., ge=0, le=100)
    reasoning: str = Field(...)


class LoanDecisionOutput(BaseModel):
    """Output from Loan Decision Agent"""
    classification: DecisionStatus = Field(...)
    risk_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=100)
    key_decision_factors: List[str] = Field(...)
    explanation: str = Field(...)


class ComplianceActionOutput(BaseModel):
    """Output from Compliance & Action Orchestrator Agent"""
    action_taken: str = Field(...)
    notification_sent: bool = Field(...)
    case_id: str = Field(...)
    timestamp: datetime = Field(...)
    summary: str = Field(...)


class FinalDecision(BaseModel):
    """Final orchestrated loan decision"""
    applicant_id: str = Field(...)
    application_status: DecisionStatus = Field(...)
    risk_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=100)

    # Component outputs
    applicant_profile: ApplicantProfileOutput = Field(...)
    financial_risk: FinancialRiskOutput = Field(...)
    loan_decision: LoanDecisionOutput = Field(...)
    compliance_action: ComplianceActionOutput = Field(...)

    # Summary
    final_explanation: str = Field(...)
    next_steps: List[str] = Field(...)

    # Metadata
    processing_timestamp: datetime = Field(...)
    processing_duration_seconds: float = Field(...)


class ApplicationStatus(BaseModel):
    """Application status query response"""
    applicant_id: str = Field(...)
    status: DecisionStatus = Field(...)
    risk_score: float = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    final_decision: Optional[FinalDecision] = Field(default=None)
