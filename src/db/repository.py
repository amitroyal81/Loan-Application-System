"""Data access layer for loan applications and decisions"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.db.models import (
    LoanApplicationModel, LoanDecisionModel,
    ApplicationStatusEnum, EmploymentTypeEnum
)

logger = logging.getLogger(__name__)


class LoanApplicationRepository:
    """Repository for loan application data access"""

    def __init__(self, db_session: Session):
        """Initialize repository with database session"""
        self.db = db_session

    def create_application(self, application_data: Dict[str, Any]) -> LoanApplicationModel:
        """Create a new loan application record"""
        try:
            employment_type = application_data.get("employment_type")
            if isinstance(employment_type, str):
                employment_type = EmploymentTypeEnum(employment_type)

            app = LoanApplicationModel(
                applicant_id=application_data["applicant_id"],
                applicant_name=application_data["applicant_name"],
                age=application_data["age"],
                income=application_data["income"],
                employment_type=employment_type,
                credit_score=application_data["credit_score"],
                loan_amount=application_data["loan_amount"],
                loan_tenure_months=application_data["loan_tenure_months"],
                existing_liabilities=application_data.get("existing_liabilities", 0),
                location=application_data["location"],
                employment_years=application_data["employment_years"],
                status=ApplicationStatusEnum.PROCESSING
            )
            self.db.add(app)
            self.db.commit()
            self.db.refresh(app)
            logger.info(f"Created application for {application_data['applicant_id']}")
            return app
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create application: {str(e)}")
            raise

    def get_application(self, applicant_id: str) -> Optional[LoanApplicationModel]:
        """Get application by applicant ID"""
        try:
            app = self.db.query(LoanApplicationModel).filter(
                LoanApplicationModel.applicant_id == applicant_id
            ).first()
            return app
        except Exception as e:
            logger.error(f"Failed to get application {applicant_id}: {str(e)}")
            raise

    def get_application_by_pk(self, app_id: int) -> Optional[LoanApplicationModel]:
        """Get application by primary key"""
        try:
            app = self.db.query(LoanApplicationModel).filter(
                LoanApplicationModel.id == app_id
            ).first()
            return app
        except Exception as e:
            logger.error(f"Failed to get application by pk {app_id}: {str(e)}")
            raise

    def application_exists(self, applicant_id: str) -> bool:
        """Check if application exists"""
        try:
            count = self.db.query(LoanApplicationModel).filter(
                LoanApplicationModel.applicant_id == applicant_id
            ).count()
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check if application exists {applicant_id}: {str(e)}")
            raise

    def update_application_status(
        self,
        applicant_id: str,
        status: str,
        risk_score: Optional[float] = None,
        error: Optional[str] = None
    ) -> LoanApplicationModel:
        """Update application status during processing"""
        try:
            app = self.get_application(applicant_id)
            if not app:
                raise ValueError(f"Application {applicant_id} not found")

            if isinstance(status, str):
                status = ApplicationStatusEnum(status)

            app.status = status
            if risk_score is not None:
                app.risk_score = risk_score
            if error is not None:
                app.error = error
            app.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(app)
            logger.info(f"Updated application {applicant_id} status to {status}")
            return app
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update application status: {str(e)}")
            raise

    def update_application_decision(
        self,
        applicant_id: str,
        final_decision: Dict[str, Any]
    ) -> LoanApplicationModel:
        """Update application with final decision"""
        try:
            app = self.get_application(applicant_id)
            if not app:
                raise ValueError(f"Application {applicant_id} not found")

            # Update application status and risk score from decision
            app_status = final_decision.get("application_status", "completed")
            if isinstance(app_status, str):
                app_status = ApplicationStatusEnum(app_status)

            app.status = app_status
            app.risk_score = final_decision.get("risk_score", 0)
            app.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(app)

            logger.info(f"Updated application {applicant_id} with decision")
            return app
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update application decision: {str(e)}")
            raise

    def list_all_applications(self, limit: int = 100, offset: int = 0) -> List[LoanApplicationModel]:
        """List all applications with pagination"""
        try:
            apps = self.db.query(LoanApplicationModel).order_by(
                desc(LoanApplicationModel.created_at)
            ).limit(limit).offset(offset).all()
            return apps
        except Exception as e:
            logger.error(f"Failed to list applications: {str(e)}")
            raise

    def get_applications_count(self) -> int:
        """Get total count of applications"""
        try:
            count = self.db.query(LoanApplicationModel).count()
            return count
        except Exception as e:
            logger.error(f"Failed to count applications: {str(e)}")
            raise


class LoanDecisionRepository:
    """Repository for loan decision data access"""

    def __init__(self, db_session: Session):
        """Initialize repository with database session"""
        self.db = db_session

    def create_decision(self, final_decision: Dict[str, Any]) -> LoanDecisionModel:
        """Create a new loan decision record"""
        try:
            decision = LoanDecisionModel(
                applicant_id=final_decision["applicant_id"],
                application_status=final_decision.get("application_status", "completed"),
                risk_score=final_decision.get("risk_score", 0),
                confidence_level=final_decision.get("confidence_level", 0),
                applicant_profile=final_decision.get("applicant_profile"),
                financial_risk=final_decision.get("financial_risk"),
                loan_decision=final_decision.get("loan_decision"),
                compliance_action=final_decision.get("compliance_action"),
                final_explanation=final_decision.get("final_explanation"),
                next_steps=final_decision.get("next_steps"),
                processing_duration_seconds=final_decision.get("processing_duration_seconds"),
                processing_timestamp=datetime.utcnow()
            )
            self.db.add(decision)
            self.db.commit()
            self.db.refresh(decision)
            logger.info(f"Created decision for {final_decision['applicant_id']}")
            return decision
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create decision: {str(e)}")
            raise

    def get_decision(self, applicant_id: str) -> Optional[LoanDecisionModel]:
        """Get decision by applicant ID"""
        try:
            decision = self.db.query(LoanDecisionModel).filter(
                LoanDecisionModel.applicant_id == applicant_id
            ).first()
            return decision
        except Exception as e:
            logger.error(f"Failed to get decision {applicant_id}: {str(e)}")
            raise

    def decision_exists(self, applicant_id: str) -> bool:
        """Check if decision exists"""
        try:
            count = self.db.query(LoanDecisionModel).filter(
                LoanDecisionModel.applicant_id == applicant_id
            ).count()
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check if decision exists {applicant_id}: {str(e)}")
            raise
