"""Financial Risk Rules Database MCP Server - Provides risk calculation and rules"""

import math
from typing import Dict, Any, List, Tuple


class RiskRulesDBServer:
    """Financial Risk Analysis Rules Server"""

    # Risk thresholds
    DTI_THRESHOLDS = {"low": 0.3, "medium": 0.5, "high": 1.0}
    CREDIT_SCORE_THRESHOLDS = {"low": 700, "medium": 650, "high": 300}
    AGE_RANGES = {"young": 25, "mid": 45, "senior": 65}

    def __init__(self):
        """Initialize risk rules"""
        self.risk_matrix = self._initialize_risk_matrix()

    def _initialize_risk_matrix(self) -> Dict[str, Dict[str, float]]:
        """Initialize risk scoring matrix"""
        return {
            "credit_score": {
                "excellent": {"range": (750, 850), "weight": 0.35},
                "good": {"range": (700, 749), "weight": 0.25},
                "fair": {"range": (650, 699), "weight": 0.15},
                "poor": {"range": (300, 649), "weight": 0.00}
            },
            "dti_ratio": {
                "excellent": {"range": (0, 0.2), "weight": 0.35},
                "good": {"range": (0.2, 0.35), "weight": 0.25},
                "fair": {"range": (0.35, 0.5), "weight": 0.15},
                "poor": {"range": (0.5, float('inf')), "weight": 0.00}
            },
            "employment_risk": {
                "low": 0.25,
                "medium": 0.5,
                "high": 0.85
            }
        }

    def calculate_debt_to_income_ratio(self, monthly_income: float, total_liabilities: float,
                                      requested_loan: float, loan_tenure_months: int) -> float:
        """
        Calculate Debt-to-Income ratio
        Returns: DTI ratio (0-1 or higher)
        """
        if monthly_income <= 0:
            return 1.0

        # Calculate estimated monthly payment for requested loan
        # Using simplified amortization formula
        monthly_rate = 0.05 / 12  # Assume 5% annual rate
        if monthly_rate > 0:
            monthly_payment = requested_loan * (monthly_rate * (1 + monthly_rate) ** loan_tenure_months) / \
                            ((1 + monthly_rate) ** loan_tenure_months - 1)
        else:
            monthly_payment = requested_loan / loan_tenure_months

        # Total monthly debt obligations
        total_monthly_debt = (total_liabilities / 12) + monthly_payment

        dti = total_monthly_debt / monthly_income
        return round(dti, 4)

    def get_credit_score_risk_level(self, credit_score: int) -> Tuple[str, float]:
        """
        Determine credit score risk level
        Returns: (risk_level, risk_score)
        """
        if credit_score >= 750:
            return ("low", 20)
        elif credit_score >= 700:
            return ("medium", 40)
        elif credit_score >= 650:
            return ("high", 60)
        else:
            return ("very_high", 85)

    def get_loan_amount_risk(self, loan_amount: float, annual_income: float) -> Tuple[str, float]:
        """
        Determine loan amount risk relative to income
        Returns: (risk_level, risk_score)
        """
        if annual_income <= 0:
            return ("high", 75)

        loan_to_income = loan_amount / annual_income

        if loan_to_income <= 2:
            return ("low", 15)
        elif loan_to_income <= 4:
            return ("medium", 45)
        elif loan_to_income <= 6:
            return ("high", 70)
        else:
            return ("very_high", 85)

    def detect_anomalies(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomalies in application data
        Returns: anomaly report with detected issues
        """
        anomalies = []
        anomaly_scores = []

        # Check age consistency with employment years
        if application_data.get("employment_years", 0) > (application_data.get("age", 0) - 18):
            anomalies.append("Employment years exceed possible work history")
            anomaly_scores.append(0.7)

        # Check income vs loan amount
        annual_income = application_data.get("income", 0) * 12
        if application_data.get("loan_amount", 0) > annual_income * 7:
            anomalies.append("Loan amount excessively high compared to annual income")
            anomaly_scores.append(0.6)

        # Check credit score vs existing liabilities
        if application_data.get("credit_score", 0) < 600 and application_data.get("existing_liabilities", 0) > 0:
            anomalies.append("Low credit score with existing high liabilities")
            anomaly_scores.append(0.5)

        # Check unemployment with substantial liabilities
        if application_data.get("employment_type") == "unemployed" and \
           application_data.get("existing_liabilities", 0) > 0:
            anomalies.append("Unemployed applicant with existing liabilities")
            anomaly_scores.append(0.8)

        max_score = max(anomaly_scores) if anomaly_scores else 0
        return {
            "anomalies_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "anomaly_score": max_score,
            "severity": "high" if max_score > 0.6 else "medium" if anomalies else "low"
        }

    def calculate_overall_risk_score(self, components: Dict[str, float]) -> float:
        """
        Calculate overall risk score from components
        Components expected: credit_score_risk, dti_risk, employment_risk, anomaly_risk
        Returns: risk score 0-100
        """
        weights = {
            "credit_score_risk": 0.35,
            "dti_risk": 0.30,
            "employment_risk": 0.20,
            "anomaly_risk": 0.15
        }

        risk_score = 0
        for component, weight in weights.items():
            if component in components:
                risk_score += components[component] * weight

        return round(min(100, risk_score), 2)

    def get_risk_level_from_score(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score < 30:
            return "low"
        elif risk_score < 60:
            return "medium"
        else:
            return "high"

    def apply_risk_rules(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply comprehensive risk rules to application
        Returns: risk assessment report
        """
        dti = self.calculate_debt_to_income_ratio(
            application_data.get("income", 0),
            application_data.get("existing_liabilities", 0),
            application_data.get("loan_amount", 0),
            application_data.get("loan_tenure_months", 12)
        )

        credit_risk, credit_score = self.get_credit_score_risk_level(
            application_data.get("credit_score", 0)
        )

        loan_risk, loan_score = self.get_loan_amount_risk(
            application_data.get("loan_amount", 0),
            application_data.get("income", 0) * 12
        )

        anomalies = self.detect_anomalies(application_data)

        # Map DTI to risk score
        if dti <= self.DTI_THRESHOLDS["low"]:
            dti_score = 20
        elif dti <= self.DTI_THRESHOLDS["medium"]:
            dti_score = 50
        else:
            dti_score = 80

        overall_risk = self.calculate_overall_risk_score({
            "credit_score_risk": credit_score,
            "dti_risk": dti_score,
            "employment_risk": 40,  # Will be enhanced by applicant profile agent
            "anomaly_risk": anomalies["anomaly_score"] * 100
        })

        return {
            "debt_to_income_ratio": dti,
            "dti_category": "acceptable" if dti <= 0.43 else "high" if dti <= 0.5 else "very_high",
            "credit_score_risk_level": credit_risk,
            "loan_amount_risk": loan_risk,
            "anomalies": anomalies,
            "overall_risk_score": overall_risk,
            "risk_level": self.get_risk_level_from_score(overall_risk),
            "detailed_breakdown": {
                "credit_score_component": credit_score,
                "dti_component": dti_score,
                "loan_amount_component": loan_score,
                "anomaly_component": anomalies["anomaly_score"] * 100
            }
        }
