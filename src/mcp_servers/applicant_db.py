"""Applicant Database MCP Server - Provides applicant profile information"""

import json
from typing import Dict, Any
from datetime import datetime
import random


class ApplicantDBServer:
    """Mock Applicant Database Server providing income stability, employment risk, credit history"""

    def __init__(self):
        """Initialize with mock applicant data"""
        self.mock_data = self._generate_mock_database()

    def _generate_mock_database(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock applicant database"""
        return {
            "APP001": {
                "name": "John Doe",
                "income_stability": {"score": 85, "trend": "stable", "volatility": 5},
                "employment_history": {"years": 5, "positions": 2, "job_changes": 1},
                "credit_history": {
                    "total_accounts": 8,
                    "active_accounts": 6,
                    "delinquencies": 0,
                    "bankruptcies": 0,
                    "avg_age_months": 48
                },
                "previous_loans": [
                    {"amount": 20000, "status": "paid_off", "tenure": 36},
                    {"amount": 5000, "status": "active", "remaining": 12}
                ]
            }
        }

    def get_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """
        Fetch applicant profile from database
        Returns income stability, employment risk details
        """
        if applicant_id not in self.mock_data:
            return self._generate_random_profile(applicant_id)

        profile = self.mock_data[applicant_id]
        return {
            "applicant_id": applicant_id,
            "name": profile.get("name", "Unknown"),
            "income_stability": profile.get("income_stability", {}),
            "employment_history": profile.get("employment_history", {}),
            "credit_history": profile.get("credit_history", {}),
            "previous_loans": profile.get("previous_loans", [])
        }

    def _generate_random_profile(self, applicant_id: str) -> Dict[str, Any]:
        """Generate random profile for demo purposes"""
        return {
            "applicant_id": applicant_id,
            "name": f"Applicant {applicant_id}",
            "income_stability": {
                "score": random.randint(60, 95),
                "trend": random.choice(["stable", "improving", "declining"]),
                "volatility": random.randint(3, 20)
            },
            "employment_history": {
                "years": random.uniform(0.5, 30),
                "positions": random.randint(1, 8),
                "job_changes": random.randint(0, 5)
            },
            "credit_history": {
                "total_accounts": random.randint(3, 15),
                "active_accounts": random.randint(2, 12),
                "delinquencies": random.randint(0, 3),
                "bankruptcies": random.randint(0, 1),
                "avg_age_months": random.randint(12, 120)
            },
            "previous_loans": [
                {
                    "amount": random.randint(5000, 100000),
                    "status": random.choice(["paid_off", "active", "charged_off"]),
                    "tenure": random.randint(12, 60)
                }
                for _ in range(random.randint(0, 3))
            ]
        }

    def calculate_income_stability_score(self, employment_history: Dict[str, Any]) -> float:
        """
        Calculate income stability score based on employment history
        Returns score 0-100
        """
        years = employment_history.get("years", 0)
        job_changes = employment_history.get("job_changes", 0)

        # Years of employment contributes 60% of score
        years_score = min(100, (years / 20) * 60)

        # Job stability (inverse of changes) contributes 40%
        job_stability_score = max(0, 40 - (job_changes * 5))

        return years_score + job_stability_score

    def get_employment_risk(self, employment_history: Dict[str, Any]) -> str:
        """
        Determine employment risk level
        Returns: 'low', 'medium', 'high'
        """
        years = employment_history.get("years", 0)
        job_changes = employment_history.get("job_changes", 0)

        if years < 1 or job_changes > 5:
            return "high"
        elif years < 2 or job_changes > 3:
            return "medium"
        else:
            return "low"

    def get_credit_history_summary(self, credit_history: Dict[str, Any]) -> str:
        """
        Generate credit history summary
        Returns: narrative description of credit profile
        """
        delinquencies = credit_history.get("delinquencies", 0)
        bankruptcies = credit_history.get("bankruptcies", 0)
        total_accounts = credit_history.get("total_accounts", 0)
        active_accounts = credit_history.get("active_accounts", 0)

        summary_parts = []

        if bankruptcies > 0:
            summary_parts.append(f"Has {bankruptcies} bankruptcy record(s)")

        if delinquencies > 0:
            summary_parts.append(f"Has {delinquencies} delinquent account(s)")
        else:
            summary_parts.append("No delinquencies on record")

        if total_accounts > 0:
            active_ratio = (active_accounts / total_accounts) * 100
            summary_parts.append(f"{active_ratio:.0f}% of {total_accounts} accounts are active")

        if not summary_parts:
            summary_parts.append("Clean credit history")

        return ". ".join(summary_parts) + "."

    def validate_application_completeness(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate application data completeness
        Returns: completeness score and any flags
        """
        required_fields = [
            "applicant_id", "applicant_name", "age", "income",
            "employment_type", "credit_score", "loan_amount",
            "loan_tenure_months", "existing_liabilities", "location"
        ]

        present_fields = sum(1 for field in required_fields if field in application_data and application_data[field])
        completeness_score = (present_fields / len(required_fields)) * 100

        flags = []
        if application_data.get("income", 0) <= 0:
            flags.append("Invalid income")
        if application_data.get("credit_score", 0) < 300:
            flags.append("Very low credit score")
        if application_data.get("age", 0) < 21:
            flags.append("Applicant below preferred age")

        return {
            "completeness_score": completeness_score,
            "flags": flags,
            "missing_fields": [f for f in required_fields if f not in application_data or not application_data[f]]
        }
