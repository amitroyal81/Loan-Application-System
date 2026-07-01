"""Compliance & Action Orchestrator Agent - Handles compliance and post-decision actions"""

import logging
from typing import Dict, Any
from datetime import datetime
import asyncio

from .base_agent import BaseAgent
from ..mcp_servers.notification_system import NotificationSystemServer

logger = logging.getLogger(__name__)


class ComplianceActionAgent(BaseAgent):
    """
    Agent responsible for compliance checks, notifications, and
    post-decision actions
    """

    def __init__(self):
        """Initialize Compliance Action Agent"""
        super().__init__("ComplianceActionAgent")
        self.notification_server = NotificationSystemServer()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance checks and post-decision actions

        Args:
            input_data: Dictionary containing:
                - applicant_id: Applicant identifier
                - decision: Loan decision (approved/rejected/manual_review)
                - risk_score: Overall risk score
                - applicant_name: Applicant name

        Returns:
            Compliance and action results
        """
        start_time = datetime.utcnow()

        # Validate input
        required_fields = ["applicant_id", "decision", "risk_score"]
        if not self._validate_input(required_fields, input_data):
            raise ValueError(f"Missing required fields for {self.agent_name}")

        applicant_id = input_data.get("applicant_id")
        decision = input_data.get("decision")
        risk_score = input_data.get("risk_score")

        # Create case
        case = await asyncio.to_thread(
            self.notification_server.create_case,
            applicant_id,
            decision,
            risk_score
        )

        case_id = case.get("case_id")

        # Execute decision-specific actions
        action_summary = await asyncio.to_thread(
            self.notification_server.execute_decision_action,
            case_id,
            decision
        )

        # Generate compliance report
        compliance_report = await asyncio.to_thread(
            self.notification_server.generate_compliance_report,
            case_id
        )

        output = {
            "applicant_id": applicant_id,
            "case_id": case_id,
            "action_taken": self._format_action_summary(decision, action_summary),
            "notification_sent": action_summary.get("notifications_sent", False),
            "actions_list": action_summary.get("actions_taken", []),
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self._generate_summary(decision, case_id, action_summary),
            "compliance_status": "verified",
            "audit_trail_items": compliance_report.get("audit_trail", {}),
            "case_status": case.get("status")
        }

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._log_execution(input_data, output, duration_ms)

        return output

    def _format_action_summary(self, decision: str, action_summary: Dict[str, Any]) -> str:
        """Format action summary"""
        actions = action_summary.get("actions_taken", [])
        notification_sent = action_summary.get("notifications_sent", False)

        action_text = ", ".join(actions) if actions else "No action"
        notification_text = "sent" if notification_sent else "not sent"

        return f"Decision {decision} executed. Actions: {action_text}. Notification {notification_text}."

    def _generate_summary(self, decision: str, case_id: str,
                         action_summary: Dict[str, Any]) -> str:
        """Generate compliance summary"""
        summary = f"Case {case_id}: {decision.upper()} decision processed. "
        summary += f"{len(action_summary.get('actions_taken', []))} action(s) initiated. "
        summary += f"Applicant notification: {'confirmed' if action_summary.get('notifications_sent') else 'pending'}. "
        summary += "All compliance requirements met. Documentation generated for audit trail."

        return summary
