"""Applicant Profile Agent - Analyzes applicant profile and history"""

import logging
from typing import Dict, Any
from datetime import datetime
import asyncio

from .base_agent import BaseAgent
from ..mcp_servers.applicant_db import ApplicantDBServer

logger = logging.getLogger(__name__)


class ApplicantProfileAgent(BaseAgent):
    """
    Agent responsible for analyzing applicant profile, income stability,
    employment history, and credit history
    """

    def __init__(self):
        """Initialize Applicant Profile Agent"""
        super().__init__("ApplicantProfileAgent")
        self.db_server = ApplicantDBServer()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute applicant profile analysis

        Args:
            input_data: Loan application data

        Returns:
            Applicant profile analysis results
        """
        start_time = datetime.utcnow()

        # Validate input
        required_fields = ["applicant_id", "age", "income", "employment_type",
                          "employment_years", "credit_score"]
        if not self._validate_input(required_fields, input_data):
            raise ValueError(f"Missing required fields for {self.agent_name}")

        applicant_id = input_data.get("applicant_id")

        # Fetch applicant profile from database
        applicant_profile = await asyncio.to_thread(
            self.db_server.get_applicant_profile, applicant_id
        )

        # Calculate income stability score
        employment_history = applicant_profile.get("employment_history", {})
        income_stability_score = await asyncio.to_thread(
            self.db_server.calculate_income_stability_score,
            employment_history
        )

        # Determine employment risk
        employment_risk = await asyncio.to_thread(
            self.db_server.get_employment_risk,
            employment_history
        )

        # Get credit history summary
        credit_history = applicant_profile.get("credit_history", {})
        credit_history_summary = await asyncio.to_thread(
            self.db_server.get_credit_history_summary,
            credit_history
        )

        # Validate application completeness
        completeness_data = await asyncio.to_thread(
            self.db_server.validate_application_completeness,
            input_data
        )

        output = {
            "applicant_id": applicant_id,
            "income_stability_score": income_stability_score,
            "employment_risk": employment_risk,
            "credit_history_summary": credit_history_summary,
            "application_completeness": completeness_data.get("completeness_score", 0),
            "flags": completeness_data.get("flags", []),
            "reasoning": self._generate_reasoning(
                income_stability_score,
                employment_risk,
                credit_history_summary,
                completeness_data
            ),
            "employment_details": {
                "years": employment_history.get("years", 0),
                "positions": employment_history.get("positions", 0),
                "type": input_data.get("employment_type")
            },
            "credit_profile": {
                "score": input_data.get("credit_score"),
                "accounts": credit_history.get("total_accounts", 0),
                "delinquencies": credit_history.get("delinquencies", 0)
            }
        }

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._log_execution(input_data, output, duration_ms)

        return output

    def _generate_reasoning(self, income_stability: float, employment_risk: str,
                           credit_summary: str, completeness: Dict[str, Any]) -> str:
        """Generate reasoning explanation for the analysis"""
        stability_desc = "stable" if income_stability > 75 else "moderate" if income_stability > 50 else "concerning"

        reasoning = f"Applicant shows {stability_desc} income stability (score: {income_stability:.0f}/100). "
        reasoning += f"Employment risk level is {employment_risk}. "
        reasoning += f"Credit profile: {credit_summary[:100]}... "

        if completeness.get("flags"):
            reasoning += f"Alerts: {', '.join(completeness['flags'][:2])}. "

        reasoning += f"Application {completeness.get('completeness_score', 0):.0f}% complete."

        return reasoning
