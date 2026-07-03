# Local MySQL Setup Guide

Your Loan Approval System is now configured to use the **local MySQL** installation on this machine.

## Current Configuration

**File**: `.env`

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Tek@12345
DB_NAME=loan_approval
```

## Verify MySQL Connection

```bash
mysql -h localhost -u root -pTek@12345 -e "SHOW DATABASES;"
```

Expected output should include `loan_approval` database.

## Start the Application

The application will automatically:
1. Connect to local MySQL
2. Create tables if they don't exist
3. Store all data in local MySQL

```bash
python main.py
```

You should see:
```
Initializing database: localhost:3306/loan_approval
Database initialized successfully
```

## Query Data from Local MySQL

### Connect to Database
```bash
mysql -h localhost -u root -pTek@12345 loan_approval
```

### Common Queries

**View all applications:**
```sql
SELECT applicant_id, applicant_name, status, risk_score, created_at 
FROM applications 
ORDER BY created_at DESC;
```

**View all decisions:**
```sql
SELECT applicant_id, application_status, confidence_level, risk_score 
FROM decisions 
ORDER BY created_at DESC;
```

**View specific applicant:**
```sql
SELECT * FROM applications WHERE applicant_id = 'APP001';
SELECT * FROM decisions WHERE applicant_id = 'APP001';
```

**Statistics:**
```sql
SELECT 
    COUNT(*) as total_applications,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
    SUM(CASE WHEN status = 'manual_review' THEN 1 ELSE 0 END) as manual_review,
    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing
FROM applications;
```

## Database Schema

### applications Table
Stores loan application data with all applicant information and processing status.

```
Columns:
- id (PRIMARY KEY)
- applicant_id (UNIQUE)
- applicant_name
- age, income, credit_score
- employment_type, employment_years
- loan_amount, loan_tenure_months
- existing_liabilities, location
- status (processing, approved, rejected, manual_review, failed, completed)
- risk_score
- error
- created_at, updated_at
```

### decisions Table
Stores final loan decisions with detailed analysis results.

```
Columns:
- id (PRIMARY KEY)
- applicant_id (UNIQUE)
- application_status
- risk_score, confidence_level
- applicant_profile (JSON)
- financial_risk (JSON)
- loan_decision (JSON)
- compliance_action (JSON)
- final_explanation (TEXT)
- next_steps (JSON)
- processing_duration_seconds
- processing_timestamp
- created_at
```

## Testing

### 1. Submit an Application
```bash
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
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

### 2. Check Status
```bash
curl http://localhost:8000/api/v1/status/APP001
```

### 3. View in MySQL
```bash
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT applicant_id, status, created_at FROM applications;"
```

### 4. Get Decision
```bash
curl http://localhost:8000/api/v1/decision/APP001
```

### 5. Check Decision in MySQL
```bash
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT applicant_id, application_status, confidence_level FROM decisions;"
```

## Troubleshooting

### "Connection refused"
MySQL is not running or port is wrong.

```bash
sudo systemctl status mysql
# or
sudo systemctl start mysql
```

### "Access denied for user 'root'"
Check credentials in `.env`. Current setup uses:
- User: `root`
- Password: `Tek@12345`

### Tables not created
Run manually:
```bash
python -c "from src.db.database import create_db_tables; create_db_tables()"
```

### Verify Connection
```bash
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;"
```

## Architecture

```
Streamlit UI / FastAPI
    ↓
API Routes (api/routes.py)
    ↓
Repository Pattern (src/db/repository.py)
    ↓
SQLAlchemy ORM (src/db/models.py)
    ↓
Local MySQL (localhost:3306)
    ↓
Tables: applications, decisions
```

## Data Flow

1. **Application Submission**: Data → API → Repository → MySQL
2. **Processing**: Orchestrator processes through agents
3. **Decision Storage**: Final decision → Decision Repository → MySQL decisions table
4. **Query**: MySQL query any time via CLI or API endpoints

All data is now persisted in your local MySQL installation!
