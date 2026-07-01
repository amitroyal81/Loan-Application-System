"""Input validation utilities"""

from typing import Dict, Any, List, Tuple


def validate_loan_application(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate loan application data
    Returns: (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    required_fields = [
        "applicant_id", "applicant_name", "age", "income",
        "employment_type", "credit_score", "loan_amount",
        "loan_tenure_months", "location"
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")

    # Age validation
    if "age" in data:
        age = data["age"]
        if not isinstance(age, (int, float)) or age < 18 or age > 120:
            errors.append("Age must be between 18 and 120")

    # Income validation
    if "income" in data:
        income = data["income"]
        if not isinstance(income, (int, float)) or income <= 0:
            errors.append("Income must be a positive number")

    # Credit score validation
    if "credit_score" in data:
        score = data["credit_score"]
        if not isinstance(score, (int, float)) or score < 300 or score > 850:
            errors.append("Credit score must be between 300 and 850")

    # Loan amount validation
    if "loan_amount" in data:
        amount = data["loan_amount"]
        if not isinstance(amount, (int, float)) or amount <= 0:
            errors.append("Loan amount must be a positive number")

    # Tenure validation
    if "loan_tenure_months" in data:
        tenure = data["loan_tenure_months"]
        if not isinstance(tenure, (int, float)) or tenure <= 0:
            errors.append("Loan tenure must be positive")

    # Employment type validation
    valid_employment_types = ["salaried", "self_employed", "freelance", "unemployed"]
    if "employment_type" in data:
        emp_type = data["employment_type"]
        if emp_type not in valid_employment_types:
            errors.append(f"Employment type must be one of: {', '.join(valid_employment_types)}")

    return len(errors) == 0, errors


def sanitize_applicant_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize applicant input data
    """
    sanitized = {}

    # Text fields - strip whitespace
    text_fields = ["applicant_id", "applicant_name", "location", "employment_type"]
    for field in text_fields:
        if field in data and data[field]:
            sanitized[field] = str(data[field]).strip()

    # Numeric fields - convert and validate
    numeric_fields = {
        "age": int,
        "income": float,
        "credit_score": int,
        "loan_amount": float,
        "loan_tenure_months": int,
        "existing_liabilities": float,
        "employment_years": float
    }

    for field, field_type in numeric_fields.items():
        if field in data and data[field] is not None:
            try:
                sanitized[field] = field_type(data[field])
            except (ValueError, TypeError):
                sanitized[field] = 0

    return sanitized


def check_missing_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
    """Check for missing fields in data"""
    return [f for f in required if f not in data or data[f] is None]
