# ✓ Local MySQL Setup Complete

Your Loan Approval System is now fully configured to use **local MySQL** instead of Docker.

## Configuration Summary

| Setting | Value |
|---------|-------|
| **Host** | localhost |
| **Port** | 3306 |
| **Database** | loan_approval |
| **User** | root |
| **Password** | Tek@12345 |
| **Status** | ✓ Connected & Tables Created |

## What Changed

1. **`.env` file updated**
   - Changed `DB_PORT` from `5432` (PostgreSQL) to `3306` (MySQL)
   - Connection now points to local MySQL installation

2. **Database layer fixed** (`src/db/database.py`)
   - Added URL encoding for password with special characters (`@`)
   - Fixed connection string parsing

3. **Tables created in MySQL**
   - ✓ `applications` table (loan applications)
   - ✓ `decisions` table (loan decisions & analysis)

## Quick Access

### Connect to Database

```bash
mysql -h localhost -u root -pTek@12345 loan_approval
```

### View All Data

```bash
# Applications
SELECT * FROM applications;

# Decisions
SELECT * FROM decisions;
```

### Complete Query Reference

See `MYSQL_QUERIES.sql` for 20+ ready-to-use queries.

## Data Persistence

**All data is now stored in your local MySQL database and will persist across application restarts.**

### Data Flow:
1. **Submit Application** → FastAPI → Repository → MySQL
2. **Process Application** → Orchestrator → Agents → Store Decision
3. **Query Data** → API Endpoints OR Direct MySQL Query

## Testing the Setup

### 1. Start the Application
```bash
python main.py
# Should show: "Database initialized successfully"
```

### 2. Submit a Test Application
```bash
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
    "applicant_name": "Test User",
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

### 3. Query MySQL Directly
```bash
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT applicant_id, status, created_at FROM applications;"
```

## Database Tables

### applications Table
```
Columns:
- id (PRIMARY KEY, auto-increment)
- applicant_id (UNIQUE)
- applicant_name
- age, income, credit_score
- employment_type, employment_years
- loan_amount, loan_tenure_months, existing_liabilities
- location
- status (ENUM: PROCESSING, APPROVED, REJECTED, MANUAL_REVIEW, FAILED, COMPLETED)
- risk_score, error
- created_at, updated_at (DATETIME)

Indexes:
- ix_applications_applicant_id (UNIQUE)
- ix_applications_created_at
```

### decisions Table
```
Columns:
- id (PRIMARY KEY, auto-increment)
- applicant_id (UNIQUE)
- application_status
- risk_score, confidence_level
- applicant_profile (JSON)
- financial_risk (JSON)
- loan_decision (JSON)
- compliance_action (JSON)
- final_explanation (TEXT)
- next_steps (JSON)
- processing_duration_seconds, processing_timestamp
- created_at (DATETIME)

Indexes:
- ix_decisions_applicant_id (UNIQUE)
- ix_decisions_created_at
```

## Common Queries

### View Recent Applications
```sql
SELECT applicant_id, applicant_name, status, risk_score, created_at 
FROM applications 
ORDER BY created_at DESC 
LIMIT 10;
```

### View Approval Statistics
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
FROM applications;
```

### Get Full Decision for Applicant
```sql
SELECT 
    a.applicant_id,
    a.applicant_name,
    d.application_status,
    d.confidence_level,
    d.risk_score,
    d.final_explanation
FROM applications a
JOIN decisions d ON a.applicant_id = d.applicant_id
WHERE a.applicant_id = 'TEST001';
```

## Architecture

```
┌─────────────────────────────────┐
│  Streamlit UI / FastAPI         │
│  (localhost:8501 / :8000)       │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  API Routes & Repository Layer  │
│  (api/routes.py)                │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  SQLAlchemy ORM                 │
│  (src/db/models.py)             │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  Local MySQL 8.0                │
│  (localhost:3306)               │
│  Database: loan_approval        │
└─────────────────────────────────┘
```

## Troubleshooting

### Connection Error: "Can't connect to MySQL server"
**Solution**: Verify MySQL is running
```bash
sudo systemctl status mysql
# or start it
sudo systemctl start mysql
```

### Error: "Access denied for user 'root'"
**Solution**: Check .env credentials
```bash
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;"
```

### Error: "Unknown database 'loan_approval'"
**Solution**: Database is auto-created on app startup. Run:
```bash
python main.py
```

### Data not appearing in MySQL
**Solution**: Ensure the app started successfully and shows "Database initialized successfully"

## Files Modified

1. **`.env`** - Updated DB_PORT to 3306
2. **`src/db/database.py`** - Fixed password URL encoding

## Files Created

1. **`SETUP_LOCAL_MYSQL.md`** - Detailed setup guide
2. **`MYSQL_QUERIES.sql`** - 20+ ready-to-use queries
3. **`LOCAL_MYSQL_SETUP_COMPLETE.md`** - This file

## Next Steps

1. ✓ Start the application: `python main.py`
2. ✓ Submit test applications via API or Streamlit
3. ✓ Query data in MySQL using the provided queries
4. ✓ Monitor data persistence across restarts

## Need Help?

### Query the database directly:
```bash
mysql -h localhost -u root -pTek@12345 loan_approval
```

### Check application logs:
```bash
grep -i "database" <logfile>
```

### Verify table creation:
```bash
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SHOW TABLES; DESCRIBE applications; DESCRIBE decisions;"
```

---

**Setup Status**: ✓ Complete and Tested
**Date**: 2026-07-01
**MySQL Version**: 8.0
**Database**: loan_approval
**Tables**: applications, decisions
