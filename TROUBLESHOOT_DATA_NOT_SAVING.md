# Troubleshooting: Data Not Saving to MySQL

**Good news**: Database saving **IS WORKING** ✓

I've verified that:
- ✓ MySQL connection works
- ✓ Tables are created correctly
- ✓ Data saves successfully
- ✓ Data can be retrieved successfully
- ✓ Updates work correctly
- ✓ Decisions are saved

If you're not seeing data, check the following:

---

## 1. Is the Application Running?

Make sure the FastAPI application is actually running:

```bash
python main.py
```

You should see:
```
INFO:     Application startup complete
Initializing database: localhost:3306/loan_approval
Database initialized successfully
```

---

## 2. Are You Submitting Applications Correctly?

### Option A: Using cURL

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

You should get a response like:
```json
{
  "status": "accepted",
  "applicant_id": "APP001",
  "message": "Application received and queued for processing",
  "created_at": "2026-07-01T23:46:50.123456"
}
```

### Option B: Using Python requests

```python
import requests

app_data = {
    "applicant_id": "APP002",
    "applicant_name": "Jane Smith",
    "age": 30,
    "income": 6000,
    "employment_type": "salaried",
    "credit_score": 750,
    "loan_amount": 75000,
    "loan_tenure_months": 60,
    "existing_liabilities": 5000,
    "location": "Texas",
    "employment_years": 3
}

response = requests.post("http://localhost:8000/api/v1/apply", json=app_data)
print(response.json())
```

### Option C: Using Streamlit UI

If using Streamlit, fill in the form and submit. The data should be saved.

---

## 3. Verify Data Was Saved

### Quick Check - Using Helper Script

```bash
./query_db.sh 1
```

This shows all applications in the database.

### Direct MySQL Check

```bash
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT applicant_id, status, created_at FROM applications ORDER BY created_at DESC LIMIT 10;"
```

### Using Python

```python
from src.db.database import get_db_session
from src.db.repository import LoanApplicationRepository

session = get_db_session()
try:
    repo = LoanApplicationRepository(session)
    apps = repo.list_all_applications(limit=10)
    for app in apps:
        print(f"{app.applicant_id}: {app.status.value}")
finally:
    session.close()
```

---

## 4. Common Issues & Solutions

### Issue: "No data in database"

**Check #1: Is MySQL running?**
```bash
sudo systemctl status mysql
# or
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;"
```

**Check #2: Is database created?**
```bash
mysql -h localhost -u root -pTek@12345 -e "SHOW DATABASES LIKE 'loan_approval';"
```

**Check #3: Are tables created?**
```bash
mysql -h localhost -u root -pTek@12345 loan_approval -e "SHOW TABLES;"
```

**Check #4: Do you have the right credentials?**
Verify `.env` has:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Tek@12345
DB_NAME=loan_approval
```

### Issue: "Application submitted but not in database"

**Possible causes:**

1. **Application not yet processed** - Background task is still running
   - Wait a few seconds and check again

2. **Wrong applicant_id** - Make sure you're searching for the right ID
   ```bash
   mysql -h localhost -u root -pTek@12345 loan_approval \
     -e "SELECT * FROM applications WHERE applicant_id='YOUR_ID';"
   ```

3. **Check application logs** - Look for errors
   ```bash
   # View logs from running application
   # Check the console output for errors
   ```

### Issue: "Database connection error"

**Error message**: "Can't connect to MySQL server"

**Solution**:
```bash
# 1. Check MySQL is running
sudo systemctl start mysql

# 2. Verify credentials
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;"

# 3. Check .env file
grep DB_ .env
```

### Issue: "UNIQUE constraint violation"

**Error message**: "Duplicate entry for applicant_id"

**Solution**: applicant_id must be unique. Use a different ID:
```bash
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{"applicant_id":"APP_UNIQUE_123",...}'
```

---

## 5. Run the Verification Test

I've created a comprehensive test script to verify everything works:

```bash
python3 test_db_save.py
```

This will:
- ✓ Verify database connection
- ✓ Check current application count
- ✓ Create a test application
- ✓ Save it to database
- ✓ Retrieve it from database
- ✓ Update its status
- ✓ Save a decision
- ✓ Retrieve the decision
- ✓ Show final count

All tests should pass with checkmarks ✓

---

## 6. Complete Workflow Test

### Terminal 1: Start the application
```bash
python main.py
```

Wait for: `Database initialized successfully`

### Terminal 2: Submit an application
```bash
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST_WORKFLOW",
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

### Terminal 2: Query the database
```bash
# Immediately after submitting
./query_db.sh 1

# Or directly
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT applicant_id, status FROM applications WHERE applicant_id='TEST_WORKFLOW';"
```

### Terminal 2: Wait a few seconds then check for decision
```bash
sleep 3

# Check if decision was created
./query_db.sh 2

# Or directly
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT applicant_id, application_status FROM decisions WHERE applicant_id='TEST_WORKFLOW';"
```

---

## 7. What Gets Saved Where

### applications table
When you submit an application, it saves:
- applicant_id (unique)
- applicant_name
- age, income, credit_score
- employment_type, employment_years
- loan_amount, loan_tenure_months, existing_liabilities
- location
- status (starts as "processing")
- created_at, updated_at

### decisions table
When processing completes, it saves:
- applicant_id
- application_status (approved/rejected/manual_review)
- risk_score, confidence_level
- Detailed JSON results from each agent
- final_explanation
- processing_duration_seconds

---

## 8. Checking Processing Status

### Check if still processing
```bash
curl http://localhost:8000/api/v1/status/TEST_WORKFLOW
```

Should show:
```json
{
  "applicant_id": "TEST_WORKFLOW",
  "status": "processing"  // or "completed", "approved", etc.
}
```

### Get final decision
```bash
curl http://localhost:8000/api/v1/decision/TEST_WORKFLOW
```

### Wait for decision
```bash
# Keep checking until decision is ready
while true; do
  curl http://localhost:8000/api/v1/decision/TEST_WORKFLOW && break
  echo "Still processing..."
  sleep 2
done
```

---

## 9. Database Schema

### applications table
```
id (INT, PRIMARY KEY, AUTO_INCREMENT)
applicant_id (VARCHAR, UNIQUE, INDEX)
applicant_name (VARCHAR)
age, income, credit_score (INT)
employment_type (ENUM)
loan_amount, loan_tenure_months (INT)
existing_liabilities (FLOAT)
location (VARCHAR)
employment_years (FLOAT)
status (ENUM)
risk_score (FLOAT, NULLABLE)
error (TEXT, NULLABLE)
created_at, updated_at (DATETIME, INDEX on created_at)
```

### decisions table
```
id (INT, PRIMARY KEY, AUTO_INCREMENT)
applicant_id (VARCHAR, UNIQUE, INDEX)
application_status (VARCHAR)
risk_score, confidence_level (FLOAT)
applicant_profile, financial_risk, loan_decision, compliance_action (JSON)
final_explanation (TEXT)
next_steps (JSON)
processing_duration_seconds (FLOAT)
processing_timestamp (DATETIME)
created_at (DATETIME, INDEX)
```

---

## 10. Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

Then run:
```bash
python main.py
```

You'll see detailed SQL queries and API logs showing:
- INSERT statements when data is saved
- SELECT statements when data is retrieved
- Connection pool info
- Processing progress

---

## Summary

✓ **Database is working correctly**
- Data saves immediately when you submit
- Data is persistent (survives restarts)
- Can query anytime

✓ **Quick verification**
```bash
# 1. Start app
python main.py

# 2. Submit application
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{"applicant_id":"TEST","applicant_name":"Test",...}'

# 3. Check database
./query_db.sh 1
```

✓ **If still having issues**:
1. Run `python3 test_db_save.py` to verify system works
2. Check MySQL is running: `sudo systemctl status mysql`
3. Verify credentials in `.env`
4. Check application logs for errors
5. Try a simple cURL request with unique applicant_id

---

**Status**: Database saving is WORKING ✓
**Next step**: Submit an application and verify with `./query_db.sh 1`
