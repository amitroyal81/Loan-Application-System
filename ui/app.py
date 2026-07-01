"""Streamlit UI for Loan Approval System Chatbot"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any
import time

# Page configuration
st.set_page_config(
    page_title="Agentic AI Loan Approval",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .success {
        color: #28a745;
        font-weight: bold;
    }
    .warning {
        color: #ffc107;
        font-weight: bold;
    }
    .danger {
        color: #dc3545;
        font-weight: bold;
    }
    .decision-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .approved {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .rejected {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    .manual-review {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

if "applications" not in st.session_state:
    st.session_state.applications = []


def get_api_url():
    """Get API base URL from config"""
    return st.session_state.api_url


def submit_application(form_data: Dict[str, Any]):
    """Submit loan application to API"""
    try:
        api_url = get_api_url()
        response = requests.post(
            f"{api_url}/api/v1/apply",
            json=form_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure FastAPI is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"❌ Error submitting application: {str(e)}")
        return None


def get_application_status(applicant_id: str):
    """Get application status from API"""
    try:
        api_url = get_api_url()
        response = requests.get(
            f"{api_url}/api/v1/status/{applicant_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.warning(f"⚠️ Application {applicant_id} not found")
        else:
            st.error(f"❌ Error fetching status: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Error fetching application status: {str(e)}")
        return None


def get_loan_decision(applicant_id: str):
    """Get loan decision from API"""
    try:
        api_url = get_api_url()
        response = requests.get(
            f"{api_url}/api/v1/decision/{applicant_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        return None
    except Exception:
        return None


def format_decision_display(decision: Dict[str, Any]):
    """Format decision for display"""
    classification = decision.get("application_status", "unknown").upper()
    risk_score = decision.get("risk_score", 0)
    confidence = decision.get("confidence_level", 0)

    # Create decision box with appropriate styling
    css_class = {
        "APPROVED": "approved",
        "REJECTED": "rejected",
        "MANUAL_REVIEW": "manual-review"
    }.get(classification, "manual-review")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Decision", classification, delta=f"{risk_score}/100 risk")

    with col2:
        st.metric("Risk Score", f"{risk_score:.1f}", delta="out of 100")

    with col3:
        st.metric("Confidence", f"{confidence:.1f}%")

    return classification, risk_score, confidence


def display_decision_details(decision: Dict[str, Any]):
    """Display detailed decision information"""
    # Display tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Decision",
        "👤 Applicant Profile",
        "💰 Financial Risk",
        "📊 Audit Trail"
    ])

    with tab1:
        st.subheader("Loan Decision Details")
        loan_decision = decision.get("loan_decision", {})

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Explanation:** {loan_decision.get('explanation', 'N/A')}")

        with col2:
            factors = loan_decision.get("key_decision_factors", [])
            if factors:
                st.write("**Key Factors:**")
                for factor in factors:
                    st.write(f"• {factor}")

        # Next steps
        next_steps = loan_decision.get("next_steps", [])
        if next_steps:
            st.write("**Next Steps:**")
            for i, step in enumerate(next_steps, 1):
                st.write(f"{i}. {step}")

    with tab2:
        st.subheader("Applicant Profile Analysis")
        applicant_profile = decision.get("applicant_profile", {})

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Income Stability Score", f"{applicant_profile.get('income_stability_score', 0):.0f}%")
            st.write(f"**Employment Risk:** {applicant_profile.get('employment_risk', 'N/A')}")

        with col2:
            st.metric("Application Completeness", f"{applicant_profile.get('application_completeness', 0):.0f}%")
            employment = applicant_profile.get("employment_details", {})
            st.write(f"**Employment Years:** {employment.get('years', 0):.1f}")

        st.write(f"**Credit History:** {applicant_profile.get('credit_history_summary', 'N/A')}")

        if applicant_profile.get("flags"):
            st.warning(f"**Flags:** {', '.join(applicant_profile['flags'])}")

    with tab3:
        st.subheader("Financial Risk Assessment")
        financial_risk = decision.get("financial_risk", {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("DTI Ratio", f"{financial_risk.get('debt_to_income_ratio', 0):.2f}")

        with col2:
            st.write(f"**Credit Score Risk:** {financial_risk.get('credit_score_risk_level', 'N/A')}")

        with col3:
            st.write(f"**Loan Amount Risk:** {financial_risk.get('loan_amount_risk', 'N/A')}")

        if financial_risk.get("anomaly_detected"):
            st.error(f"**⚠️ Anomalies Detected:** {financial_risk.get('anomaly_details', 'Unknown anomalies')}")

    with tab4:
        st.subheader("Processing Details")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Case ID:** {decision.get('case_id', 'N/A')}")
            st.write(f"**Processing Time:** {decision.get('processing_duration_seconds', 0):.2f}s")

        with col2:
            st.write(f"**Timestamp:** {decision.get('processing_timestamp', 'N/A')}")
            st.write(f"**Workflow State:** {decision.get('workflow_state', 'N/A')}")

        # Final explanation
        st.text_area(
            "**Final Explanation:**",
            value=decision.get("final_explanation", "No explanation available"),
            height=200,
            disabled=True
        )


# Main UI
st.markdown('<div class="header">', unsafe_allow_html=True)
st.title("🏦 Agentic AI Loan Approval System")
st.markdown("_Intelligent Multi-Agent Loan Decision Engine_")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Configuration
    with st.expander("API Settings"):
        api_url = st.text_input(
            "API URL",
            value=st.session_state.api_url,
            help="Base URL of the FastAPI server"
        )
        st.session_state.api_url = api_url

        if st.button("🔗 Test Connection"):
            try:
                response = requests.get(f"{api_url}/api/v1/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Connected to API successfully!")
                else:
                    st.error(f"❌ API returned status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

    # Navigation
    st.subheader("📌 Navigation")
    page = st.radio(
        "Select Page:",
        ["🆕 New Application", "📋 Check Status", "📈 Metrics"],
        label_visibility="collapsed"
    )

# Main content
if page == "🆕 New Application":
    st.subheader("Submit New Loan Application")

    with st.form("loan_application_form"):
        col1, col2 = st.columns(2)

        with col1:
            applicant_id = st.text_input(
                "Applicant ID",
                value=f"APP{int(time.time()) % 100000}",
                help="Unique identifier for the applicant"
            )
            applicant_name = st.text_input("Full Name", placeholder="John Doe")
            age = st.number_input("Age", min_value=18, max_value=120, value=35)
            income = st.number_input("Monthly Income ($)", min_value=0, value=5000, step=100)
            employment_type = st.selectbox(
                "Employment Type",
                ["salaried", "self_employed", "freelance", "unemployed"]
            )

        with col2:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=720)
            loan_amount = st.number_input("Loan Amount ($)", min_value=0, value=50000, step=1000)
            loan_tenure = st.number_input("Loan Tenure (Months)", min_value=1, value=60, step=1)
            existing_liabilities = st.number_input("Existing Liabilities ($)", min_value=0, value=10000, step=1000)
            employment_years = st.number_input("Years of Employment", min_value=0.0, value=5.0, step=0.5)

        location = st.text_input("Location/State", placeholder="California")

        submit_button = st.form_submit_button("📨 Submit Application", use_container_width=True)

    if submit_button:
        # Validate form
        if not applicant_name or not location:
            st.error("❌ Please fill in all required fields")
        else:
            with st.spinner("📤 Submitting application..."):
                application_data = {
                    "applicant_id": applicant_id,
                    "applicant_name": applicant_name,
                    "age": age,
                    "income": income,
                    "employment_type": employment_type,
                    "credit_score": credit_score,
                    "loan_amount": loan_amount,
                    "loan_tenure_months": loan_tenure,
                    "existing_liabilities": existing_liabilities,
                    "location": location,
                    "employment_years": employment_years
                }

                result = submit_application(application_data)

                if result:
                    st.session_state.applications.append({
                        "applicant_id": applicant_id,
                        "name": applicant_name,
                        "submitted_at": datetime.now().isoformat()
                    })

                    st.success(f"✅ Application submitted successfully!")
                    st.info(f"**Applicant ID:** {applicant_id}\n\n**Status:** Processing\n\nYour application is being evaluated by our multi-agent AI system. Check back in a few moments for the decision.")

                    # Store for quick access
                    st.session_state.check_applicant_id = applicant_id

elif page == "📋 Check Status":
    st.subheader("Check Application Status")

    # Search for application
    col1, col2 = st.columns([3, 1])

    with col1:
        applicant_id = st.text_input(
            "Enter Applicant ID",
            placeholder="e.g., APP123456",
            label_visibility="collapsed"
        )

    with col2:
        check_button = st.button("🔍 Check", use_container_width=True)

    if check_button and applicant_id:
        with st.spinner(f"Fetching status for {applicant_id}..."):
            status = get_application_status(applicant_id)

            if status:
                st.subheader(f"Application: {applicant_id}")

                # Display status
                status_value = status.get("status", "unknown").upper()
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Status", status_value)

                with col2:
                    st.metric("Risk Score", f"{status.get('risk_score', 0):.1f}/100")

                with col3:
                    created_at = status.get("created_at", "N/A")
                    st.write(f"**Submitted:** {created_at}")

                # Check if decision is available
                if status.get("final_decision"):
                    st.success("✅ Decision Available!")

                    decision = status.get("final_decision")
                    format_decision_display(decision)

                    st.divider()

                    display_decision_details(decision)

                else:
                    st.info("⏳ Decision is still being processed. Please check back in a moment.")

                    # Polling option
                    if st.button("🔄 Refresh"):
                        st.rerun()

elif page == "📈 Metrics":
    st.subheader("System Metrics & Analytics")

    try:
        response = requests.get(f"{get_api_url()}/api/v1/metrics", timeout=10)
        metrics = response.json()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Applicant Analyses", metrics.get("applicant_agent_executions", 0))

        with col2:
            st.metric("Risk Assessments", metrics.get("risk_agent_executions", 0))

        with col3:
            st.metric("Decisions Made", metrics.get("decision_agent_executions", 0))

        with col4:
            st.metric("Compliances Processed", metrics.get("compliance_agent_executions", 0))

        st.divider()

        # Application history
        st.subheader("Application Submissions")
        response = requests.get(f"{get_api_url()}/api/v1/applications", timeout=10)
        app_list = response.json()

        if app_list.get("applications"):
            st.write(f"**Total Applications:** {app_list.get('total', 0)}")

            applications_df = []
            for app in app_list.get("applications", [])[:10]:
                applications_df.append({
                    "Applicant ID": app["applicant_id"],
                    "Status": app["status"].upper(),
                    "Created": app["created_at"]
                })

            st.dataframe(applications_df, use_container_width=True)
        else:
            st.info("No applications yet")

    except Exception as e:
        st.error(f"❌ Error fetching metrics: {str(e)}")

# Footer
st.divider()
st.markdown("""
---
**Agentic AI Intelligent Loan Approval System** v1.0.0
- Multi-Agent Architecture with LangGraph Orchestration
- Powered by Claude Sonnet 4.6
- Model Context Protocol (MCP) for Agent Communication
""")
