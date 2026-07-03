# Local MySQL Database - Quick Start Guide

## ✓ Your system is now configured to use LOCAL MySQL

Your Loan Approval System has been successfully configured to persist all data in your **local MySQL installation** (not Docker).

---

## Quick Commands

### 1. **Start the Application**
```bash
python main.py
```
Expected output: `Database initialized successfully`

### 2. **Query Data Directly**

#### Using Helper Script
```bash
# View recent applications
./query_db.sh 3

# View approval statistics
./query_db.sh 4

# Connect to MySQL CLI
./query_db.sh 12
```

#### Using MySQL CLI
```bash
mysql -h localhost -u root -pTek@12345 loan_approval

# Inside MySQL, try:
SELECT * FROM applications;
SELECT * FROM decisions;
```

### 3. **Submit Test Application**
```bash
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST_001",
    "applicant_name": "John Doe",
    "age": 35,
    "income": 5000,
    "employment_type": "salaried",
    "credit_score": 720,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "existing_liabilities": 10000,
    "location": "California",
    "employment_years": 5
  }'
```

---

## Database Configuration

| Setting | Value |
|---------|-------|
| Host | localhost |
| Port | 3306 |
| Database | loan_approval |
| User | root |
| Password | Tek@12345 |

**Location**: `.env` file in project root

---

## Query Examples

### View All Applications
```sql
SELECT applicant_id, applicant_name, status, risk_score, created_at 
FROM applications 
ORDER BY created_at DESC;
```

### View All Decisions
```sql
SELECT applicant_id, application_status, confidence_level, risk_score 
FROM decisions 
ORDER BY created_at DESC;
```

### Approval Statistics
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status='APPROVED' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status='REJECTED' THEN 1 ELSE 0 END) as rejected
FROM applications;
```

### Get Full Details for One Applicant
```sql
SELECT 
    a.applicant_id,
    a.applicant_name,
    a.status,
    d.application_status,
    d.confidence_level,
    d.final_explanation
FROM applications a
LEFT JOIN decisions d ON a.applicant_id = d.applicant_id
WHERE a.applicant_id = 'TEST_001';
```

---

## Helper Script Usage

```bash
./query_db.sh          # Show menu
./query_db.sh 1        # View all applications
./query_db.sh 2        # View all decisions
./query_db.sh 3        # View recent applications
./query_db.sh 4        # Approval statistics
./query_db.sh 5        # High-risk applications
./query_db.sh 6        # Low-confidence decisions
./query_db.sh 7        # Join applications & decisions
./query_db.sh 8        # By employment type
./query_db.sh 9 APP001 # Search specific applicant
./query_db.sh 10       # Performance stats
./query_db.sh 11       # Count records
./query_db.sh 12       # MySQL CLI
```

---

## Database Schema

### applications Table
- `id` - Primary key
- `applicant_id` - Unique identifier (searchable)
- `applicant_name` - Name of applicant
- `age, income, credit_score` - Financial info
- `employment_type, employment_years` - Employment info
- `loan_amount, loan_tenure_months` - Loan details
- `status` - Processing status (PROCESSING, APPROVED, REJECTED, MANUAL_REVIEW, FAILED, COMPLETED)
- `risk_score` - Calculated risk
- `created_at, updated_at` - Timestamps

### decisions Table
- `id` - Primary key
- `applicant_id` - Unique identifier (links to applications)
- `application_status` - Final decision
- `risk_score, confidence_level` - Decision metrics
- `applicant_profile, financial_risk, loan_decision, compliance_action` - JSON results from agents
- `final_explanation` - Decision summary
- `processing_duration_seconds` - Time taken
- `created_at` - When decision was made

---

## Data Flow

```
User submits application via API
    ↓
FastAPI receives and validates
    ↓
Repository stores in MySQL applications table
    ↓
Orchestrator processes through agents
    ↓
Decision stored in MySQL decisions table
    ↓
User can query anytime via:
  - API endpoints
  - MySQL CLI
  - Helper script
  - Any MySQL client
```

---

## Verification

Check that everything is working:

```bash
# 1. MySQL is running
sudo systemctl status mysql

# 2. Database exists
mysql -h localhost -u root -pTek@12345 -e "SHOW DATABASES LIKE 'loan_approval';"

# 3. Tables exist
mysql -h localhost -u root -pTek@12345 loan_approval -e "SHOW TABLES;"

# 4. Tables have correct structure
mysql -h localhost -u root -pTek@12345 loan_approval -e "DESCRIBE applications; DESCRIBE decisions;"
```

---

## Troubleshooting

### MySQL Connection Error
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL if not running
sudo systemctl start mysql

# Test connection
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;"
```

### "Unknown database" error
Database will be created automatically when the app starts:
```bash
python main.py
```

### "Access denied" error
Verify credentials in `.env`:
```bash
grep DB_ .env
```

### Data not persisting
1. Check app shows "Database initialized successfully"
2. Verify MySQL is running
3. Check `.env` has correct credentials

---

## Files Created/Modified

### Created
- `SETUP_LOCAL_MYSQL.md` - Detailed setup guide
- `MYSQL_QUERIES.sql` - 20+ ready-to-use queries
- `LOCAL_MYSQL_SETUP_COMPLETE.md` - Full documentation
- `README_LOCAL_MYSQL.md` - This file
- `query_db.sh` - Helper script for queries

### Modified
- `.env` - Updated DB_PORT from 5432 to 3306
- `src/db/database.py` - Fixed password URL encoding

---

## API Endpoints

Your FastAPI automatically stores data in MySQL:

- `POST /api/v1/apply` - Submit application (stores in DB)
- `GET /api/v1/status/{applicant_id}` - Check status (reads from DB)
- `GET /api/v1/decision/{applicant_id}` - Get decision (reads from DB)
- `GET /api/v1/applications` - List all (reads from DB)
- `GET /api/v1/metrics` - System metrics (reads from DB)

---

## Next Steps

1. ✓ Start application: `python main.py`
2. ✓ Submit applications via API or Streamlit UI
3. ✓ Query data using:
   - `./query_db.sh` (easy)
   - `mysql` CLI (direct)
   - API endpoints (programmatic)
4. ✓ Data persists across restarts

---

## Example: End-to-End Test

```bash
# 1. Terminal 1: Start the app
python main.py

# 2. Terminal 2: Submit application
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{"applicant_id":"TEST001","applicant_name":"John","age":35,"income":5000,"employment_type":"salaried","credit_score":720,"loan_amount":50000,"loan_tenure_months":60,"existing_liabilities":10000,"location":"CA","employment_years":5}'

# 3. Terminal 2: View in database
./query_db.sh 1

# 4. Terminal 2: Get decision
curl http://localhost:8000/api/v1/decision/TEST001

# 5. Terminal 2: View decisions
./query_db.sh 2
```

---

## MySQL Persistence

✓ **All data is persisted in MySQL**

- Applications are saved when submitted
- Decisions are saved when processed
- Data survives application restarts
- Multiple application instances can share the same data
- Full ACID compliance
- Queryable anytime

---

## Support

For detailed information, see:
- `SETUP_LOCAL_MYSQL.md` - Setup details
- `MYSQL_QUERIES.sql` - SQL query reference
- `LOCAL_MYSQL_SETUP_COMPLETE.md` - Complete documentation
- `.env` - Configuration

---

**Status**: ✓ Ready to Use
**Database**: localhost:3306/loan_approval
**User**: root
**Last Updated**: 2026-07-01
