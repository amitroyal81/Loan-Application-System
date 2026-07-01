"""Financial Risk Analysis Agent - Analyzes financial risk indicators"""

import logging
from typing import Dict, Any
from datetime import datetime
import asyncio

from .base_agent import BaseAgent
from ..mcp_servers.risk_rules_db import RiskRulesDBServer

logger = logging.getLogger(__name__)


class FinancialRiskAgent(BaseAgent):
    """
    Agent responsible for financial risk analysis including
    debt-to-income ratio, credit score risk, anomaly detection
    """

    def __init__(self):
        """Initialize Financial Risk Agent"""
        super().__init__("FinancialRiskAgent")
        self.risk_server = RiskRulesDBServer()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute financial risk analysis

        Args:
            input_data: Loan application data

        Returns:
            Financial risk analysis results
        """
        start_time = datetime.utcnow()

        # Validate input
        required_fields = ["applicant_id", "income", "loan_amount",
                          "loan_tenure_months", "existing_liabilities", "credit_score"]
        if not self._validate_input(required_fields, input_data):
            raise ValueError(f"Missing required fields for {self.agent_name}")

        # Calculate DTI ratio
        dti = await asyncio.to_thread(
            self.risk_server.calculate_debt_to_income_ratio,
            input_data.get("income", 0),
            input_data.get("existing_liabilities", 0),
            input_data.get("loan_amount", 0),
            input_data.get("loan_tenure_months", 12)
        )

        # Get credit score risk level
        credit_risk, credit_score = await asyncio.to_thread(
            self.risk_server.get_credit_score_risk_level,
            input_data.get("credit_score", 0)
        )

        # Detect anomalies
        anomalies = await asyncio.to_thread(
            self.risk_server.detect_anomalies,
            input_data
        )

        # Apply comprehensive risk rules
        risk_assessment = await asyncio.to_thread(
            self.risk_server.apply_risk_rules,
            input_data
        )

        output = {
            "applicant_id": input_data.get("applicant_id"),
            "debt_to_income_ratio": dti,
            "credit_score_risk_level": credit_risk,
            "loan_amount_risk": risk_assessment.get("loan_amount_risk"),
            "anomaly_detected": anomalies.get("anomalies_detected", False),
            "anomaly_details": "; ".join(anomalies.get("anomalies", [])) if anomalies.get("anomalies") else None,
            "risk_score": risk_assessment.get("overall_risk_score", 50),
            "risk_level": risk_assessment.get("risk_level", "medium"),
            "reasoning": self._generate_reasoning(
                dti,
                credit_risk,
                anomalies,
                risk_assessment
            ),
            "detailed_breakdown": risk_assessment.get("detailed_breakdown", {}),
            "dti_category": risk_assessment.get("dti_category")
        }

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._log_execution(input_data, output, duration_ms)

        return output

    def _generate_reasoning(self, dti: float, credit_risk: str,
                           anomalies: Dict[str, Any],
                           risk_assessment: Dict[str, Any]) -> str:
        """Generate reasoning explanation for the analysis"""
        reasoning = f"Debt-to-Income ratio: {dti:.2f} (category: {risk_assessment.get('dti_category')}). "
        reasoning += f"Credit score risk level: {credit_risk}. "
        reasoning += f"Loan amount risk: {risk_assessment.get('loan_amount_risk')}. "

        if anomalies.get("anomalies_detected"):
            reasoning += f"Anomalies detected: {anomalies['severity']} severity. "
            if anomalies.get("anomalies"):
                reasoning += f"Issues: {'; '.join(anomalies['anomalies'][:2])}. "

        reasoning += f"Overall risk score: {risk_assessment.get('overall_risk_score', 50)}/100 ({risk_assessment.get('risk_level')})."

        return reasoning
