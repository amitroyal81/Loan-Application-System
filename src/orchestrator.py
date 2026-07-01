"""LangGraph-based orchestration engine for multi-agent loan approval workflow"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from .agents import (
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceActionAgent
)

logger = logging.getLogger(__name__)


class OrchestratorState(str, Enum):
    """Orchestration workflow states"""
    INITIALIZED = "initialized"
    APPLICANT_PROFILE = "applicant_profile"
    FINANCIAL_RISK = "financial_risk"
    DECISION = "decision"
    COMPLIANCE = "compliance"
    COMPLETED = "completed"
    FAILED = "failed"


class LoanApprovalOrchestrator:
    """
    Main orchestration engine coordinating all agents using a state machine pattern.
    Simulates LangGraph StateGraph for deterministic multi-agent orchestration.
    """

    def __init__(self):
        """Initialize orchestrator with all agents"""
        self.applicant_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceActionAgent()

        self.workflow_history = []
        self.current_state = OrchestratorState.INITIALIZED

    async def process_loan_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - processes complete loan application
        through all agents and returns final decision

        Args:
            application_data: Loan application details

        Returns:
            Complete decision with all agent outputs
        """
        start_time = datetime.utcnow()
        applicant_id = application_data.get("applicant_id", "unknown")

        try:
            logger.info(f"Starting loan approval process for {applicant_id}")

            # State 1: Applicant Profile Analysis
            self.current_state = OrchestratorState.APPLICANT_PROFILE
            logger.info(f"State: {self.current_state} - Analyzing applicant profile")

            applicant_output = await self.applicant_agent.execute(application_data)
            self._record_workflow_step(applicant_id, "applicant_profile", applicant_output)

            # State 2: Financial Risk Analysis
            self.current_state = OrchestratorState.FINANCIAL_RISK
            logger.info(f"State: {self.current_state} - Analyzing financial risk")

            risk_output = await self.risk_agent.execute(application_data)
            self._record_workflow_step(applicant_id, "financial_risk", risk_output)

            # State 3: Loan Decision
            self.current_state = OrchestratorState.DECISION
            logger.info(f"State: {self.current_state} - Synthesizing decision")

            decision_input = {
                "applicant_id": applicant_id,
                "applicant_profile": applicant_output,
                "financial_risk": risk_output,
                "application_data": application_data
            }
            decision_output = await self.decision_agent.execute(decision_input)
            self._record_workflow_step(applicant_id, "decision", decision_output)

            # State 4: Compliance & Actions
            self.current_state = OrchestratorState.COMPLIANCE
            logger.info(f"State: {self.current_state} - Processing compliance")

            compliance_input = {
                "applicant_id": applicant_id,
                "decision": decision_output.get("classification"),
                "risk_score": decision_output.get("risk_score"),
                "applicant_name": application_data.get("applicant_name", "Unknown")
            }
            compliance_output = await self.compliance_agent.execute(compliance_input)
            self._record_workflow_step(applicant_id, "compliance", compliance_output)

            # State 5: Complete
            self.current_state = OrchestratorState.COMPLETED
            logger.info(f"State: {self.current_state} - Loan approval process completed")

            # Synthesize final response
            final_response = self._synthesize_final_response(
                application_data,
                applicant_output,
                risk_output,
                decision_output,
                compliance_output,
                start_time
            )

            return final_response

        except Exception as e:
            self.current_state = OrchestratorState.FAILED
            logger.error(f"Loan approval process failed for {applicant_id}: {str(e)}")
            raise

    def _synthesize_final_response(self,
                                  application_data: Dict[str, Any],
                                  applicant_output: Dict[str, Any],
                                  risk_output: Dict[str, Any],
                                  decision_output: Dict[str, Any],
                                  compliance_output: Dict[str, Any],
                                  start_time: datetime) -> Dict[str, Any]:
        """
        Synthesize all agent outputs into final decision response
        """
        processing_duration = (datetime.utcnow() - start_time).total_seconds()

        final_response = {
            "applicant_id": application_data.get("applicant_id"),
            "application_status": decision_output.get("classification"),
            "risk_score": decision_output.get("risk_score"),
            "confidence_level": decision_output.get("confidence_level"),

            # Component outputs for transparency
            "applicant_profile": applicant_output,
            "financial_risk": risk_output,
            "loan_decision": decision_output,
            "compliance_action": compliance_output,

            # Summary
            "final_explanation": self._generate_final_explanation(decision_output),
            "next_steps": decision_output.get("next_steps", []),

            # Metadata
            "processing_timestamp": datetime.utcnow().isoformat(),
            "processing_duration_seconds": round(processing_duration, 2),
            "case_id": compliance_output.get("case_id"),
            "workflow_state": self.current_state.value
        }

        return final_response

    def _generate_final_explanation(self, decision_output: Dict[str, Any]) -> str:
        """Generate comprehensive final explanation"""
        explanation = decision_output.get("explanation", "")
        factors = decision_output.get("key_decision_factors", [])

        if factors:
            explanation += f"\n\nKey Factors:\n"
            for i, factor in enumerate(factors[:5], 1):
                explanation += f"{i}. {factor}\n"

        conditions = decision_output.get("approval_conditions", {})
        if conditions and decision_output.get("classification") == "approved":
            rate = conditions.get("final_interest_rate")
            explanation += f"\n\nProposed Terms:\nInterest Rate: {rate}%\n"
            explanation += conditions.get("loan_terms_recommendation", "")

        return explanation

    def _record_workflow_step(self, applicant_id: str, step_name: str,
                            step_output: Dict[str, Any]) -> None:
        """Record workflow step for audit trail"""
        workflow_record = {
            "applicant_id": applicant_id,
            "step": step_name,
            "timestamp": datetime.utcnow().isoformat(),
            "state": self.current_state.value,
            "output_keys": list(step_output.keys()) if step_output else []
        }
        self.workflow_history.append(workflow_record)
        logger.debug(f"Workflow step recorded: {workflow_record}")

    def get_workflow_history(self, applicant_id: Optional[str] = None) -> list:
        """Get workflow history, optionally filtered by applicant"""
        if applicant_id:
            return [h for h in self.workflow_history if h.get("applicant_id") == applicant_id]
        return self.workflow_history

    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get execution metrics from all agents"""
        return {
            "applicant_agent_executions": len(self.applicant_agent.get_execution_history()),
            "risk_agent_executions": len(self.risk_agent.get_execution_history()),
            "decision_agent_executions": len(self.decision_agent.get_execution_history()),
            "compliance_agent_executions": len(self.compliance_agent.get_execution_history()),
            "workflow_steps": len(self.workflow_history),
            "current_state": self.current_state.value
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_state": self.current_state.value,
            "agents_initialized": {
                "applicant_agent": bool(self.applicant_agent),
                "risk_agent": bool(self.risk_agent),
                "decision_agent": bool(self.decision_agent),
                "compliance_agent": bool(self.compliance_agent)
            },
            "metrics": self.get_execution_metrics()
        }
