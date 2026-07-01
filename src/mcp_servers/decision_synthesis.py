"""Decision Synthesis MCP Server - Makes final loan decisions"""

from typing import Dict, Any, List, Tuple
from enum import Enum


class DecisionType(str, Enum):
    """Loan decision types"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class DecisionSynthesisServer:
    """Decision synthesis engine for loan approval"""

    # Decision rules thresholds
    APPROVAL_RISK_THRESHOLD = 40
    REJECTION_RISK_THRESHOLD = 75
    MANUAL_REVIEW_CONFIDENCE_THRESHOLD = 70

    def __init__(self):
        """Initialize decision synthesis engine"""
        self.decision_rules = self._load_decision_rules()

    def _load_decision_rules(self) -> Dict[str, Any]:
        """Load decision-making rules"""
        return {
            "approve": {
                "max_risk_score": 40,
                "min_credit_score": 650,
                "max_dti": 0.43,
                "min_income_stability": 60
            },
            "reject": {
                "min_risk_score": 75,
                "max_credit_score": 600,
                "max_dti": 0.60,
                "min_income_stability": 30
            },
            "manual_review": {
                "min_confidence": 0.7
            }
        }

    def synthesize_decision(self,
                          applicant_profile: Dict[str, Any],
                          financial_risk: Dict[str, Any],
                          risk_score: float) -> Dict[str, Any]:
        """
        Synthesize final decision from all agent inputs
        Returns: decision with classification and reasoning
        """
        decision_type = self._determine_decision(applicant_profile, financial_risk, risk_score)
        confidence = self._calculate_confidence(applicant_profile, financial_risk, decision_type)
        factors = self._extract_key_factors(applicant_profile, financial_risk)

        return {
            "classification": decision_type,
            "risk_score": risk_score,
            "confidence_level": confidence,
            "key_decision_factors": factors,
            "explanation": self._generate_explanation(decision_type, risk_score, factors),
            "decision_timestamp": True
        }

    def _determine_decision(self, applicant_profile: Dict[str, Any],
                           financial_risk: Dict[str, Any],
                           risk_score: float) -> DecisionType:
        """
        Determine decision type based on risk scores and profiles
        """
        # Clear rejection criteria
        if self._should_reject(applicant_profile, financial_risk, risk_score):
            return DecisionType.REJECTED

        # Clear approval criteria
        if self._should_approve(applicant_profile, financial_risk, risk_score):
            return DecisionType.APPROVED

        # Marginal cases go to manual review
        return DecisionType.MANUAL_REVIEW

    def _should_reject(self, applicant_profile: Dict[str, Any],
                      financial_risk: Dict[str, Any],
                      risk_score: float) -> bool:
        """Determine if application should be rejected"""
        if risk_score >= self.REJECTION_RISK_THRESHOLD:
            return True

        if applicant_profile.get("flags", []):
            if any(flag in applicant_profile.get("flags", []) for flag in ["Very low credit score", "Applicant below preferred age"]):
                if risk_score > 65:
                    return True

        if financial_risk.get("anomaly_detected"):
            if financial_risk.get("anomaly_details", "").startswith("Unemployed"):
                return True

        return False

    def _should_approve(self, applicant_profile: Dict[str, Any],
                       financial_risk: Dict[str, Any],
                       risk_score: float) -> bool:
        """Determine if application should be approved"""
        if risk_score > self.APPROVAL_RISK_THRESHOLD:
            return False

        income_stability = applicant_profile.get("income_stability_score", 0)
        if income_stability < 50:
            return False

        employment_risk = applicant_profile.get("employment_risk")
        if employment_risk == "high":
            return False

        dti = financial_risk.get("debt_to_income_ratio", 0)
        if dti > 0.43:
            return False

        return risk_score <= self.APPROVAL_RISK_THRESHOLD and income_stability >= 60

    def _calculate_confidence(self, applicant_profile: Dict[str, Any],
                            financial_risk: Dict[str, Any],
                            decision_type: DecisionType) -> float:
        """
        Calculate confidence level in decision
        Returns: 0-100 confidence score
        """
        confidence = 50  # Base confidence

        # Increase confidence based on data quality
        if applicant_profile.get("application_completeness", 0) > 90:
            confidence += 15

        # Increase confidence based on stable profile
        if applicant_profile.get("income_stability_score", 0) > 75:
            confidence += 10

        # Decrease confidence for anomalies
        if financial_risk.get("anomaly_detected"):
            confidence -= 20

        # Adjust based on decision type
        if decision_type == DecisionType.APPROVED:
            if applicant_profile.get("income_stability_score", 0) > 80:
                confidence += 15
        elif decision_type == DecisionType.REJECTED:
            if financial_risk.get("anomaly_detected"):
                confidence += 10

        return min(100, max(0, confidence))

    def _extract_key_factors(self, applicant_profile: Dict[str, Any],
                            financial_risk: Dict[str, Any]) -> List[str]:
        """Extract key decision factors"""
        factors = []

        # Credit-related factors
        credit_history = applicant_profile.get("credit_history_summary", "")
        if "No delinquencies" in credit_history:
            factors.append("Clean credit history")
        if "bankruptcy" in credit_history.lower():
            factors.append("Previous bankruptcy on record")

        # Employment factors
        employment_risk = applicant_profile.get("employment_risk")
        if employment_risk == "low":
            factors.append("Stable employment")
        elif employment_risk == "high":
            factors.append("Employment instability risk")

        # Financial factors
        dti = financial_risk.get("debt_to_income_ratio", 0)
        if dti < 0.3:
            factors.append("Strong debt-to-income ratio")
        elif dti > 0.5:
            factors.append("High debt-to-income ratio")

        # Income stability
        income_stability = applicant_profile.get("income_stability_score", 0)
        if income_stability > 80:
            factors.append("High income stability")

        # Anomalies
        if financial_risk.get("anomaly_detected"):
            anomalies = financial_risk.get("anomaly_details", "")
            if anomalies:
                factors.append(f"Anomaly detected: {anomalies}")

        return factors[:5]  # Top 5 factors

    def _generate_explanation(self, decision_type: DecisionType,
                             risk_score: float,
                             factors: List[str]) -> str:
        """Generate human-readable explanation of decision"""
        explanations = {
            DecisionType.APPROVED: f"Application approved based on low risk profile (score: {risk_score}/100). Key strengths: {', '.join(factors[:2])}",
            DecisionType.REJECTED: f"Application rejected due to high risk indicators (score: {risk_score}/100). Concerns: {', '.join(factors[:2])}",
            DecisionType.MANUAL_REVIEW: f"Application requires manual review (score: {risk_score}/100). Factors: {', '.join(factors[:2])}"
        }
        return explanations.get(decision_type, "Decision pending review")

    def generate_approval_conditions(self, applicant_profile: Dict[str, Any],
                                    financial_risk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate approval conditions if application is approved or conditional
        """
        conditions = {
            "base_interest_rate": 5.0,  # Base rate in %
            "adjustments": []
        }

        # Adjust based on credit score risk
        credit_risk = financial_risk.get("credit_score_risk_level", "medium")
        if credit_risk == "low":
            conditions["adjustments"].append({"type": "credit_score_discount", "value": -0.5})
        elif credit_risk == "high":
            conditions["adjustments"].append({"type": "credit_score_premium", "value": 1.5})

        # Adjust based on DTI
        dti = financial_risk.get("debt_to_income_ratio", 0)
        if dti > 0.4:
            conditions["adjustments"].append({"type": "dti_premium", "value": 0.75})

        # Calculate final rate
        final_rate = conditions["base_interest_rate"]
        for adjustment in conditions["adjustments"]:
            final_rate += adjustment["value"]

        conditions["final_interest_rate"] = round(final_rate, 2)
        conditions["loan_terms_recommendation"] = f"Approve at {conditions['final_interest_rate']}% APR with quarterly income verification"

        return conditions

    def get_next_steps(self, decision_type: DecisionType) -> List[str]:
        """Get recommended next steps based on decision"""
        steps = {
            DecisionType.APPROVED: [
                "Review final loan terms",
                "Prepare documents for signature",
                "Schedule disbursement",
                "Set up payment reminders"
            ],
            DecisionType.REJECTED: [
                "Send rejection letter with reasoning",
                "Provide appeal process information",
                "Recommend credit improvement steps"
            ],
            DecisionType.MANUAL_REVIEW: [
                "Assign to loan officer for review",
                "Request additional documentation if needed",
                "Schedule follow-up call with applicant",
                "Escalate to senior management if needed"
            ]
        }
        return steps.get(decision_type, [])
