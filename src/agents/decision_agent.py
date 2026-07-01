"""Loan Decision Agent - Makes final loan decision"""

import logging
from typing import Dict, Any
from datetime import datetime
import asyncio

from .base_agent import BaseAgent
from ..mcp_servers.decision_synthesis import DecisionSynthesisServer

logger = logging.getLogger(__name__)


class LoanDecisionAgent(BaseAgent):
    """
    Agent responsible for making final loan decision by synthesizing
    outputs from other agents
    """

    def __init__(self):
        """Initialize Loan Decision Agent"""
        super().__init__("LoanDecisionAgent")
        self.decision_server = DecisionSynthesisServer()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute loan decision synthesis

        Args:
            input_data: Dictionary containing:
                - applicant_profile: Output from ApplicantProfileAgent
                - financial_risk: Output from FinancialRiskAgent
                - application_data: Original application data

        Returns:
            Loan decision results
        """
        start_time = datetime.utcnow()

        # Validate input
        required_fields = ["applicant_profile", "financial_risk"]
        if not self._validate_input(required_fields, input_data):
            raise ValueError(f"Missing required fields for {self.agent_name}")

        applicant_profile = input_data.get("applicant_profile", {})
        financial_risk = input_data.get("financial_risk", {})
        risk_score = financial_risk.get("risk_score", 50)

        # Synthesize decision
        decision = await asyncio.to_thread(
            self.decision_server.synthesize_decision,
            applicant_profile,
            financial_risk,
            risk_score
        )

        # Get approval conditions if applicable
        approval_conditions = await asyncio.to_thread(
            self.decision_server.generate_approval_conditions,
            applicant_profile,
            financial_risk
        )

        # Get next steps
        next_steps = await asyncio.to_thread(
            self.decision_server.get_next_steps,
            decision.get("classification")
        )

        output = {
            "applicant_id": input_data.get("applicant_id"),
            "classification": decision.get("classification").value,
            "risk_score": decision.get("risk_score"),
            "confidence_level": decision.get("confidence_level"),
            "key_decision_factors": decision.get("key_decision_factors", []),
            "explanation": decision.get("explanation"),
            "approval_conditions": approval_conditions,
            "next_steps": next_steps,
            "reasoning": self._generate_final_reasoning(
                decision,
                applicant_profile,
                financial_risk
            )
        }

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._log_execution(input_data, output, duration_ms)

        return output

    def _generate_final_reasoning(self, decision: Dict[str, Any],
                                 applicant_profile: Dict[str, Any],
                                 financial_risk: Dict[str, Any]) -> str:
        """Generate comprehensive final reasoning"""
        classification = decision.get("classification", "unknown").upper()
        confidence = decision.get("confidence_level", 0)

        reasoning = f"Decision: {classification} (Confidence: {confidence:.0f}%). "
        reasoning += f"Key factors: {'; '.join(decision.get('key_decision_factors', [])[:3])}. "

        if decision.get("classification").value == "approved":
            conditions = decision.get("approval_conditions", {})
            reasoning += f"Recommended rate: {conditions.get('final_interest_rate', 'N/A')}%."

        reasoning += f" Risk score: {financial_risk.get('risk_score')}/100."

        return reasoning
