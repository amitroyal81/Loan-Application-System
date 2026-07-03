#!/bin/bash

# Database query helper script for Loan Approval System
# Usage: ./query_db.sh [query_name]

DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="Tek@12345"
DB_NAME="loan_approval"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run query
run_query() {
    local query="$1"
    local description="$2"

    echo -e "${BLUE}➜ $description${NC}"
    echo -e "${YELLOW}Query:${NC} $query"
    echo ""

    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "$query"
    echo ""
}

# Show menu if no argument provided
if [ -z "$1" ]; then
    echo -e "${GREEN}Loan Approval System - Database Query Helper${NC}"
    echo ""
    echo "Usage: $0 [query_option]"
    echo ""
    echo "Options:"
    echo "  1  - View all applications"
    echo "  2  - View all decisions"
    echo "  3  - View recent applications (last 10)"
    echo "  4  - Approval statistics"
    echo "  5  - High-risk applications (risk > 60)"
    echo "  6  - Low-confidence decisions (< 70%)"
    echo "  7  - Join applications with decisions"
    echo "  8  - Applications by employment type"
    echo "  9  - Search specific applicant (requires APP_ID)"
    echo "  10 - Performance stats"
    echo "  11 - Count all records"
    echo "  12 - Connect to MySQL CLI"
    echo ""
    exit 0
fi

# Execute selected query
case "$1" in
    1)
        run_query \
            "SELECT applicant_id, applicant_name, status, risk_score, income, credit_score, loan_amount, created_at FROM applications ORDER BY created_at DESC;" \
            "All Applications"
        ;;
    2)
        run_query \
            "SELECT applicant_id, application_status, risk_score, confidence_level, processing_duration_seconds, created_at FROM decisions ORDER BY created_at DESC;" \
            "All Decisions"
        ;;
    3)
        run_query \
            "SELECT applicant_id, applicant_name, status, risk_score, created_at FROM applications ORDER BY created_at DESC LIMIT 10;" \
            "Recent Applications (Last 10)"
        ;;
    4)
        run_query \
            "SELECT COUNT(*) as total, SUM(CASE WHEN status='APPROVED' THEN 1 ELSE 0 END) as approved, SUM(CASE WHEN status='REJECTED' THEN 1 ELSE 0 END) as rejected, SUM(CASE WHEN status='MANUAL_REVIEW' THEN 1 ELSE 0 END) as manual_review FROM applications;" \
            "Approval Statistics"
        ;;
    5)
        run_query \
            "SELECT applicant_id, applicant_name, risk_score, income, credit_score, status FROM applications WHERE risk_score > 60 ORDER BY risk_score DESC;" \
            "High-Risk Applications (Risk Score > 60)"
        ;;
    6)
        run_query \
            "SELECT applicant_id, confidence_level, risk_score, application_status FROM decisions WHERE confidence_level < 70 ORDER BY confidence_level ASC;" \
            "Low-Confidence Decisions (< 70%)"
        ;;
    7)
        run_query \
            "SELECT a.applicant_id, a.applicant_name, a.status, a.risk_score, d.application_status, d.confidence_level FROM applications a LEFT JOIN decisions d ON a.applicant_id = d.applicant_id ORDER BY a.created_at DESC;" \
            "Join Applications with Decisions"
        ;;
    8)
        run_query \
            "SELECT employment_type, COUNT(*) as count, ROUND(AVG(risk_score), 2) as avg_risk_score, ROUND(AVG(credit_score), 2) as avg_credit_score FROM applications GROUP BY employment_type;" \
            "Applications by Employment Type"
        ;;
    9)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Usage: $0 9 <APPLICANT_ID>${NC}"
            echo "Example: $0 9 APP001"
            exit 1
        fi
        run_query \
            "SELECT * FROM applications WHERE applicant_id = '$2'; SELECT * FROM decisions WHERE applicant_id = '$2';" \
            "Details for Applicant $2"
        ;;
    10)
        run_query \
            "SELECT COUNT(*) as total_decisions, ROUND(AVG(processing_duration_seconds), 2) as avg_time_sec, ROUND(AVG(confidence_level), 2) as avg_confidence FROM decisions;" \
            "Processing Performance Statistics"
        ;;
    11)
        run_query \
            "SELECT 'applications' as table_name, COUNT(*) as count FROM applications UNION ALL SELECT 'decisions', COUNT(*) FROM decisions;" \
            "Total Record Count"
        ;;
    12)
        echo -e "${GREEN}Connecting to MySQL CLI...${NC}"
        echo "Command: mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME"
        echo ""
        mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME"
        ;;
    *)
        echo -e "${YELLOW}Invalid option: $1${NC}"
        echo "Run: $0 (with no arguments) to see all options"
        exit 1
        ;;
esac
