# Quick Start: MySQL Database Integration

## 60-Second Setup (Using Docker)

### 1. Start MySQL
```bash
docker run --name loan-mysql -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=loan_approval -e MYSQL_USER=admin \
  -e MYSQL_PASSWORD=password -p 3306:3306 -d mysql:8.0
```

### 2. Update `.env`
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=password
DB_NAME=loan_approval
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Application
```bash
python main.py
```

You should see:
```
Initializing database: localhost:3306/loan_approval
Database initialized successfully
```

## Testing

### 1. Submit Application
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

### 3. Verify in Database
```bash
mysql -h localhost -u admin -ppassword loan_approval \
  -e "SELECT applicant_id, status, created_at FROM applications;"
```

### 4. List All Applications
```bash
curl http://localhost:8000/api/v1/applications
```

## Key Changes

| What | Before | After |
|------|--------|-------|
| Storage | Python dict (in-memory) | MySQL database |
| Persistence | Lost on restart | Survives restarts |
| Multiple instances | Not supported | Supported |
| Scalability | Limited | Unlimited |
| Data fallback | None | In-memory fallback |

## Database Tables Created

```
applications:  applicant_id, status, risk_score, created_at, ...
decisions:     applicant_id, application_status, confidence_level, ...
```

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│ Streamlit UI / FastAPI Endpoints                │
├─────────────────────────────────────────────────┤
│ API Routes (api/routes.py)                      │
│ ├─ Repository Pattern for Data Access          │
│ └─ In-Memory Fallback for Backwards Compat      │
├─────────────────────────────────────────────────┤
│ Repository Layer (src/db/repository.py)         │
│ ├─ LoanApplicationRepository                    │
│ └─ LoanDecisionRepository                       │
├─────────────────────────────────────────────────┤
│ SQLAlchemy ORM (src/db/models.py)               │
├─────────────────────────────────────────────────┤
│ Database (MySQL)                                │
│ ├─ applications table                           │
│ └─ decisions table                              │
└─────────────────────────────────────────────────┘
```

## File Structure

```
src/db/                           # ← NEW Database layer
├── __init__.py
├── models.py                      # SQLAlchemy ORM models
├── database.py                    # Connection management
└── repository.py                  # Data access layer

Modified:
├── api/routes.py                  # Uses repository instead of dict
├── src/config.py                  # Added DB config
├── main.py                        # Initialize DB on startup
└── requirements.txt               # Added sqlalchemy, pymysql
```

## Configuration

All database settings are in `.env`:

```env
# Default values (change as needed)
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=password
DB_NAME=loan_approval
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Make sure MySQL is running: `docker ps` |
| "Unknown database" | Database was not created (normal, auto-created) |
| "Access denied" | Check DB_USER and DB_PASSWORD in `.env` |
| Data lost on restart | Verify "Database initialized successfully" in logs |

## Next Steps

1. **Read Full Guide**: See `DATABASE_SETUP.md` for complete documentation
2. **Understand Architecture**: Check `MIGRATION_SUMMARY.md` for technical details
3. **Run Tests**: `pytest tests/ -v`
4. **Deploy**: Follow production guidelines in `DATABASE_SETUP.md`

## Quick Queries

Connect to database:
```bash
mysql -h localhost -u admin -ppassword loan_approval
```

View applications:
```sql
SELECT * FROM applications;
SELECT * FROM decisions;
```

## What's Working

✅ Submit applications → Stored in MySQL  
✅ Check status → Read from MySQL  
✅ Get decisions → Read from MySQL  
✅ List applications → Query from MySQL  
✅ System metrics → Count from MySQL  
✅ Backwards compatible → Falls back to in-memory if needed  

## Support

- See `DATABASE_SETUP.md` for detailed troubleshooting
- Check application logs for database initialization status
- View MIGRATION_SUMMARY.md for architecture details
