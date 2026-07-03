"""Streamlit UI for Loan Approval System - Banking Industry Standard"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any
import time

# Page configuration
st.set_page_config(
    page_title="Loan Approval Platform | Financial Services",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Banking Industry Standard CSS
st.markdown("""
    <style>
    /* Banking Color Scheme */
    :root {
        --primary-blue: #003D82;
        --secondary-blue: #0052CC;
        --accent-green: #17A038;
        --warning-orange: #FF9500;
        --danger-red: #E31C23;
        --light-gray: #F5F7FA;
        --medium-gray: #E8EAED;
        --dark-gray: #202124;
        --text-primary: #202124;
        --text-secondary: #5F6368;
    }

    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    }

    /* Main Layout */
    .main {
        padding: 0;
        background-color: #FFFFFF;
    }

    /* Header Styling */
    .bank-header {
        background: linear-gradient(135deg, #003D82 0%, #0052CC 100%);
        color: white;
        padding: 2rem 3rem;
        margin: 0;
        border-bottom: 3px solid #17A038;
    }

    .bank-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .bank-header p {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.95;
    }

    /* Card Styling */
    .bank-card {
        background: white;
        border: 1px solid #E8EAED;
        border-radius: 8px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: box-shadow 0.3s ease;
    }

    .bank-card:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }

    .bank-card h3 {
        color: #003D82;
        font-size: 1.1rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #F5F7FA;
    }

    /* Status Indicators */
    .status-approved {
        background-color: #E8F5E9;
        border-left: 4px solid #17A038;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .status-rejected {
        background-color: #FFEBEE;
        border-left: 4px solid #E31C23;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .status-pending {
        background-color: #FFF8E1;
        border-left: 4px solid #FF9500;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .status-manual-review {
        background-color: #E3F2FD;
        border-left: 4px solid #0052CC;
        padding: 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    /* Form Styling */
    .form-section {
        background: white;
        border: 1px solid #E8EAED;
        border-radius: 8px;
        padding: 2rem;
        margin: 1.5rem 0;
    }

    .form-section h4 {
        color: #003D82;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #F5F7FA;
    }

    /* Metrics/KPI Styling */
    .kpi-card {
        background: white;
        border: 1px solid #E8EAED;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }

    .kpi-card h4 {
        color: #5F6368;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-card .value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #003D82;
        margin: 0.5rem 0;
    }

    .kpi-card .subtitle {
        color: #5F6368;
        font-size: 0.8rem;
        margin: 0.5rem 0 0 0;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #0052CC 0%, #003D82 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }

    /* Success/Error Messages */
    .success-message {
        background-color: #E8F5E9;
        color: #1B5E20;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 4px solid #17A038;
        margin: 1rem 0;
    }

    .error-message {
        background-color: #FFEBEE;
        color: #B71C1C;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 4px solid #E31C23;
        margin: 1rem 0;
    }

    .warning-message {
        background-color: #FFF8E1;
        color: #F57F17;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 4px solid #FF9500;
        margin: 1rem 0;
    }

    .info-message {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 4px solid #0052CC;
        margin: 1rem 0;
    }

    /* Footer */
    .bank-footer {
        background-color: #F5F7FA;
        border-top: 1px solid #E8EAED;
        padding: 2rem 3rem;
        text-align: center;
        color: #5F6368;
        font-size: 0.85rem;
        margin-top: 3rem;
    }

    /* Navigation Styling */
    .nav-item {
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .nav-item:hover {
        background-color: #F5F7FA;
    }

    /* Table Styling */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
    }

    .dataframe td, .dataframe th {
        padding: 1rem;
        border-bottom: 1px solid #E8EAED;
        text-align: left;
    }

    .dataframe th {
        background-color: #F5F7FA;
        color: #003D82;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    /* Divider */
    .divider {
        border: none;
        border-top: 1px solid #E8EAED;
        margin: 2rem 0;
    }

    /* Sidebar */
    .sidebar {
        background-color: #F5F7FA;
    }

    [data-testid="stSidebarNav"] {
        background-color: #F5F7FA;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

if "applications" not in st.session_state:
    st.session_state.applications = []

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False


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


# Main UI - Banking Header
st.markdown("""
<div class="bank-header">
    <h1>🏦 Loan Approval Platform</h1>
    <p>Intelligent Digital Lending Solution | Powered by Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)

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
    st.markdown("""
    <div style="padding: 0 2rem;">
        <h2 style="color: #003D82; margin-bottom: 0.5rem;">New Loan Application</h2>
        <p style="color: #5F6368; margin-bottom: 2rem;">Fill in your details to apply for a loan. All fields are required.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        with st.form("loan_application_form"):
            # Applicant Information Section
            st.markdown("""
            <div style="background-color: #F5F7FA; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
                <h4 style="color: #003D82; margin: 0;">Personal Information</h4>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                applicant_id = st.text_input(
                    "Applicant ID",
                    value=f"APP{int(time.time()) % 100000}",
                    help="Unique identifier for the applicant",
                    disabled=True
                )
            with col2:
                applicant_name = st.text_input("Full Name *", placeholder="John Doe")
            with col3:
                age = st.number_input("Age *", min_value=18, max_value=120, value=35)

            col1, col2, col3 = st.columns(3)
            with col1:
                employment_type = st.selectbox(
                    "Employment Type *",
                    ["salaried", "self_employed", "freelance", "unemployed"]
                )
            with col2:
                employment_years = st.number_input("Years of Employment *", min_value=0.0, value=5.0, step=0.5)
            with col3:
                location = st.text_input("Location/State *", placeholder="California")

            st.divider()

            # Financial Information Section
            st.markdown("""
            <div style="background-color: #F5F7FA; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
                <h4 style="color: #003D82; margin: 0;">Financial Information</h4>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                income = st.number_input("Monthly Income ($) *", min_value=0, value=5000, step=100)
            with col2:
                credit_score = st.number_input("Credit Score *", min_value=300, max_value=850, value=720)
            with col3:
                existing_liabilities = st.number_input("Existing Liabilities ($) *", min_value=0, value=10000, step=1000)

            st.divider()

            # Loan Details Section
            st.markdown("""
            <div style="background-color: #F5F7FA; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
                <h4 style="color: #003D82; margin: 0;">Loan Details</h4>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                loan_amount = st.number_input("Loan Amount ($) *", min_value=0, value=50000, step=1000)
            with col2:
                loan_tenure = st.number_input("Loan Tenure (Months) *", min_value=1, value=60, step=1)

            st.divider()

            # Button layout with submit, reset, and cancel
            button_col1, button_col2, button_col3 = st.columns(3)

            with button_col1:
                submit_button = st.form_submit_button(
                    "✓ Submit Application",
                    use_container_width=True,
                    help="Submit your loan application for processing"
                )

            with button_col2:
                reset_button = st.form_submit_button(
                    "↻ Reset Form",
                    use_container_width=True,
                    help="Clear all fields and start over"
                )

            with button_col3:
                cancel_button = st.form_submit_button(
                    "✕ Cancel",
                    use_container_width=True,
                    help="Cancel application and return to dashboard"
                )

        # Handle button actions
        if submit_button:
            # Validate form
            if not applicant_name or not location:
                st.markdown("""
                <div class="error-message">
                    ⚠ Please fill in all required fields (marked with *)
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("Processing your application..."):
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

                        st.markdown("""
                        <div class="success-message">
                            ✓ Application submitted successfully
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="info-message" style="margin-top: 1rem;">
                            <strong>Application Reference:</strong> {applicant_id}<br>
                            <strong>Status:</strong> Under Review<br>
                            <strong>Next Step:</strong> Your application is being evaluated. Check back shortly for the decision.
                        </div>
                        """, unsafe_allow_html=True)

                        # Store for quick access
                        st.session_state.check_applicant_id = applicant_id
                        st.session_state.form_submitted = True

        elif reset_button:
            st.markdown("""
            <div class="warning-message">
                ↻ Form has been reset to default values
            </div>
            """, unsafe_allow_html=True)
            st.rerun()

        elif cancel_button:
            st.markdown("""
            <div class="warning-message">
                ✕ Application cancelled
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

elif page == "📋 Check Status":
    st.markdown("""
    <div style="padding: 0 2rem;">
        <h2 style="color: #003D82; margin-bottom: 0.5rem;">Application Status</h2>
        <p style="color: #5F6368; margin-bottom: 2rem;">Enter your application reference number to check the status</p>
    </div>
    """, unsafe_allow_html=True)

    # Search for application
    st.markdown("""
    <div class="form-section">
        <h4>Find Your Application</h4>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        applicant_id = st.text_input(
            "Application Reference Number",
            placeholder="e.g., APP123456",
            label_visibility="collapsed"
        )

    with col2:
        check_button = st.button("Search", use_container_width=True, help="Search for your application")

    if check_button and applicant_id:
        with st.spinner(f"Searching for application {applicant_id}..."):
            status = get_application_status(applicant_id)

            if status:
                st.markdown(f"""
                <div style="padding: 0 2rem;">
                    <h3 style="color: #003D82; margin-bottom: 1.5rem;">Application: {applicant_id}</h3>
                </div>
                """, unsafe_allow_html=True)

                # Display status
                status_value = status.get("status", "unknown").upper()
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    status_color = {
                        "PROCESSING": "#FF9500",
                        "APPROVED": "#17A038",
                        "REJECTED": "#E31C23",
                        "MANUAL_REVIEW": "#0052CC",
                        "COMPLETED": "#17A038"
                    }.get(status_value, "#5F6368")

                    st.markdown(f"""
                    <div class="kpi-card">
                        <h4>Status</h4>
                        <div class="value" style="color: {status_color};">
                            {status_value}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <h4>Risk Score</h4>
                        <div class="value">{status.get('risk_score', 0):.1f}</div>
                        <div class="subtitle">Out of 100</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    created_at = status.get("created_at", "N/A")
                    st.markdown(f"""
                    <div class="kpi-card">
                        <h4>Submitted</h4>
                        <div class="subtitle">{created_at}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    updated_at = status.get("updated_at", "N/A")
                    st.markdown(f"""
                    <div class="kpi-card">
                        <h4>Last Updated</h4>
                        <div class="subtitle">{updated_at}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Check if decision is available
                if status.get("final_decision"):
                    st.markdown("""
                    <div class="success-message" style="margin-top: 2rem;">
                        ✓ Decision Available - Your application has been reviewed
                    </div>
                    """, unsafe_allow_html=True)

                    decision = status.get("final_decision")
                    format_decision_display(decision)

                    st.divider()

                    display_decision_details(decision)

                else:
                    st.markdown("""
                    <div class="warning-message" style="margin-top: 2rem;">
                        ⏳ Decision Pending - Your application is under review. Please check back shortly.
                    </div>
                    """, unsafe_allow_html=True)

                    # Polling option
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button("↻ Refresh Status", use_container_width=True):
                            st.rerun()

elif page == "📈 Metrics":
    st.markdown("""
    <div style="padding: 0 2rem;">
        <h2 style="color: #003D82; margin-bottom: 0.5rem;">Dashboard & Metrics</h2>
        <p style="color: #5F6368; margin-bottom: 2rem;">System performance and application overview</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        response = requests.get(f"{get_api_url()}/api/v1/metrics", timeout=10)
        metrics = response.json()

        # KPI Section
        st.markdown("""
        <div style="padding: 0 2rem;">
            <h3 style="color: #003D82; margin-bottom: 1.5rem;">Key Performance Indicators</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Applicants Analyzed</h4>
                <div class="value">{metrics.get("applicant_agent_executions", 0)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Risk Assessments</h4>
                <div class="value">{metrics.get("risk_agent_executions", 0)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Decisions Made</h4>
                <div class="value">{metrics.get("decision_agent_executions", 0)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <h4>Compliance Processed</h4>
                <div class="value">{metrics.get("compliance_agent_executions", 0)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Application history
        st.markdown("""
        <div style="padding: 0 2rem;">
            <h3 style="color: #003D82; margin-bottom: 1.5rem;">Recent Applications</h3>
        </div>
        """, unsafe_allow_html=True)

        response = requests.get(f"{get_api_url()}/api/v1/applications", timeout=10)
        app_list = response.json()

        if app_list.get("applications"):
            st.markdown(f"""
            <div style="padding: 0 2rem; margin-bottom: 1rem;">
                <strong style="color: #003D82;">Total Applications: {app_list.get('total', 0)}</strong>
            </div>
            """, unsafe_allow_html=True)

            applications_df = []
            for app in app_list.get("applications", [])[:10]:
                applications_df.append({
                    "Application ID": app["applicant_id"],
                    "Status": app["status"].upper(),
                    "Submitted": app["created_at"]
                })

            st.dataframe(applications_df, use_container_width=True)
        else:
            st.markdown("""
            <div class="info-message">
                ℹ No applications submitted yet
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
            ⚠ Error fetching metrics: {str(e)}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="bank-footer">
    <strong>Loan Approval Platform</strong> v1.0.0<br>
    <span style="font-size: 0.8rem;">
        Powered by Advanced AI Analytics | Multi-Agent Architecture<br>
        © 2026 Financial Services. All rights reserved.
    </span>
</div>
""", unsafe_allow_html=True)
