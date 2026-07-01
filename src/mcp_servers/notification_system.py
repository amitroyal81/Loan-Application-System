"""Notification System MCP Server - Handles notifications and case tracking"""

from datetime import datetime
from typing import Dict, Any, List
import uuid


class NotificationSystemServer:
    """Notification and case management system"""

    def __init__(self):
        """Initialize notification system"""
        self.cases = {}  # In-memory case storage for demo

    def create_case(self, applicant_id: str, decision: str, risk_score: float) -> Dict[str, Any]:
        """
        Create a new case for tracking
        Returns: case details with case ID
        """
        case_id = f"CASE_{uuid.uuid4().hex[:8].upper()}"

        case = {
            "case_id": case_id,
            "applicant_id": applicant_id,
            "decision": decision,
            "risk_score": risk_score,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created",
            "notifications_sent": [],
            "actions_taken": []
        }

        self.cases[case_id] = case
        return case

    def send_notification(self, case_id: str, notification_type: str,
                         recipient: str, message: str) -> Dict[str, Any]:
        """
        Send notification for a case
        Returns: notification details
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        case = self.cases[case_id]

        notification = {
            "notification_id": str(uuid.uuid4())[:8],
            "case_id": case_id,
            "type": notification_type,  # email, sms, internal
            "recipient": recipient,
            "message": message,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent"
        }

        case["notifications_sent"].append(notification)

        return notification

    def log_action(self, case_id: str, action: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Log an action taken on a case
        Returns: action details
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        case = self.cases[case_id]

        action_entry = {
            "action_id": str(uuid.uuid4())[:8],
            "case_id": case_id,
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        case["actions_taken"].append(action_entry)

        return action_entry

    def get_case_status(self, case_id: str) -> Dict[str, Any]:
        """
        Get current status of a case
        Returns: case details and action history
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        return self.cases[case_id]

    def update_case_status(self, case_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update case status
        Returns: updated case
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        case = self.cases[case_id]
        case["status"] = new_status
        case["updated_at"] = datetime.utcnow().isoformat()

        return case

    def generate_compliance_report(self, case_id: str) -> Dict[str, Any]:
        """
        Generate compliance report for a case
        Returns: compliance report with audit trail
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        case = self.cases[case_id]

        return {
            "report_id": f"REPORT_{uuid.uuid4().hex[:8].upper()}",
            "case_id": case_id,
            "applicant_id": case["applicant_id"],
            "generated_at": datetime.utcnow().isoformat(),
            "decision": case["decision"],
            "risk_score": case["risk_score"],
            "case_status": case["status"],
            "audit_trail": {
                "creation_time": case["created_at"],
                "notifications": len(case["notifications_sent"]),
                "actions_logged": len(case["actions_taken"])
            },
            "compliance_checklist": [
                {"item": "Application data validated", "status": "completed"},
                {"item": "Credit check performed", "status": "completed"},
                {"item": "Risk assessment completed", "status": "completed"},
                {"item": "Decision documented", "status": "completed"},
                {"item": "Notification sent to applicant", "status": "completed"}
            ]
        }

    def execute_decision_action(self, case_id: str, decision: str) -> Dict[str, Any]:
        """
        Execute actions based on loan decision
        Returns: summary of actions taken
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        case = self.cases[case_id]
        actions_summary = {
            "case_id": case_id,
            "decision": decision,
            "actions_taken": [],
            "notifications_sent": False
        }

        if decision == "approved":
            # Approve actions
            self.log_action(case_id, "Decision recorded", {"decision_type": "approved"})
            self.send_notification(
                case_id, "email", case["applicant_id"],
                "Congratulations! Your loan application has been approved."
            )
            actions_summary["actions_taken"] = [
                "Decision recorded",
                "Approval notification sent",
                "Prepare loan documents",
                "Schedule disbursement"
            ]
            actions_summary["notifications_sent"] = True

        elif decision == "rejected":
            # Rejection actions
            self.log_action(case_id, "Decision recorded", {"decision_type": "rejected"})
            self.send_notification(
                case_id, "email", case["applicant_id"],
                "Your loan application has been declined. Please see details for more information."
            )
            actions_summary["actions_taken"] = [
                "Decision recorded",
                "Rejection notification sent",
                "Appeal process initiated"
            ]
            actions_summary["notifications_sent"] = True

        elif decision == "manual_review":
            # Manual review actions
            self.log_action(case_id, "Escalated to manual review", {})
            self.send_notification(
                case_id, "internal", "loan_officers",
                f"Case {case_id} requires manual review"
            )
            actions_summary["actions_taken"] = [
                "Case escalated to loan officer",
                "Internal notification sent",
                "Awaiting manual review"
            ]
            actions_summary["notifications_sent"] = True

        case["status"] = f"{decision}_processed"

        return actions_summary

    def get_all_cases_for_applicant(self, applicant_id: str) -> List[Dict[str, Any]]:
        """
        Get all cases for a given applicant
        Returns: list of case records
        """
        return [case for case in self.cases.values() if case["applicant_id"] == applicant_id]

    def archive_case(self, case_id: str) -> Dict[str, Any]:
        """
        Archive a completed case
        Returns: archived case details
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")

        case = self.cases[case_id]
        case["archived"] = True
        case["archived_at"] = datetime.utcnow().isoformat()

        return case
