"""SQLAlchemy ORM models for loan approval system"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
import enum
import json

Base = declarative_base()


class ApplicationStatusEnum(str, enum.Enum):
    """Application status enumeration"""
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    FAILED = "failed"
    COMPLETED = "completed"


class EmploymentTypeEnum(str, enum.Enum):
    """Employment type enumeration"""
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    FREELANCE = "freelance"
    UNEMPLOYED = "unemployed"


class LoanApplicationModel(Base):
    """Loan application database model"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(String(255), unique=True, nullable=False, index=True)
    applicant_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    employment_type = Column(SQLEnum(EmploymentTypeEnum), nullable=False)
    credit_score = Column(Integer, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    existing_liabilities = Column(Float, default=0, nullable=False)
    location = Column(String(255), nullable=False)
    employment_years = Column(Float, nullable=False)

    # Processing status
    status = Column(SQLEnum(ApplicationStatusEnum), default=ApplicationStatusEnum.PROCESSING, nullable=False)
    risk_score = Column(Float, nullable=True)
    error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "applicant_name": self.applicant_name,
            "age": self.age,
            "income": self.income,
            "employment_type": self.employment_type.value if isinstance(self.employment_type, EmploymentTypeEnum) else self.employment_type,
            "credit_score": self.credit_score,
            "loan_amount": self.loan_amount,
            "loan_tenure_months": self.loan_tenure_months,
            "existing_liabilities": self.existing_liabilities,
            "location": self.location,
            "employment_years": self.employment_years,
            "status": self.status.value if isinstance(self.status, ApplicationStatusEnum) else self.status,
            "risk_score": self.risk_score,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class LoanDecisionModel(Base):
    """Loan decision database model"""
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(String(255), unique=True, nullable=False, index=True)
    application_status = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)

    # JSON fields for complex nested data
    applicant_profile = Column(JSON, nullable=True)
    financial_risk = Column(JSON, nullable=True)
    loan_decision = Column(JSON, nullable=True)
    compliance_action = Column(JSON, nullable=True)
    final_explanation = Column(Text, nullable=True)
    next_steps = Column(JSON, nullable=True)

    # Processing metadata
    processing_duration_seconds = Column(Float, nullable=True)
    processing_timestamp = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "application_status": self.application_status,
            "risk_score": self.risk_score,
            "confidence_level": self.confidence_level,
            "applicant_profile": self.applicant_profile,
            "financial_risk": self.financial_risk,
            "loan_decision": self.loan_decision,
            "compliance_action": self.compliance_action,
            "final_explanation": self.final_explanation,
            "next_steps": self.next_steps,
            "processing_duration_seconds": self.processing_duration_seconds,
            "processing_timestamp": self.processing_timestamp.isoformat() if self.processing_timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
