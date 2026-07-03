# MySQL Database Migration Summary

## What Changed

The Agentic AI Loan Approval System has been successfully migrated from in-memory Python dictionaries to persistent MySQL database storage.

### Before (In-Memory Only)
- All loan applications stored in Python `Dict` in `application_store`
- Data lost on application restart
- Could not scale to multiple instances
- No persistence between deployments

### After (MySQL + Backwards-Compatible In-Memory Fallback)
- All loan applications persisted in MySQL `applications` table
- All decisions stored in MySQL `decisions` table
- Data survives application restarts
- Supports multi-instance deployments
- Maintains backwards compatibility with in-memory fallback

## New Files Created

### Database Layer (`src/db/`)
1. **`__init__.py`** - Package marker
2. **`models.py`** - SQLAlchemy ORM models
   - `LoanApplicationModel` - Maps to `applications` table
   - `LoanDecisionModel` - Maps to `decisions` table
   - `ApplicationStatusEnum` - Application status options
   - `EmploymentTypeEnum` - Employment type options

3. **`database.py`** - Database configuration & connection management
   - `init_db_engine()` - Initializes SQLAlchemy engine with connection pooling
   - `create_db_tables()` - Creates database schema on startup
   - `get_db_session()` - Gets new database session
   - `close_db_connection()` - Closes all connections on shutdown

4. **`repository.py`** - Data access abstraction layer
   - `LoanApplicationRepository` - CRUD operations for applications
     - `create_application()`
     - `get_application()`
     - `update_application_status()`
     - `update_application_decision()`
     - `list_all_applications()`
     - `get_applications_count()`
   - `LoanDecisionRepository` - CRUD operations for decisions
     - `create_decision()`
     - `get_decision()`
     - `decision_exists()`

## Modified Files

### `requirements.txt`
- ✅ Added `sqlalchemy==2.0.23` - ORM framework
- ✅ Added `pymysql==1.1.0` - MySQL Python driver
- ✅ Added `alembic==1.13.0` - Database migrations tool

### `src/config.py`
- ✅ Added database configuration fields:
  - `db_host` - MySQL host (default: "localhost")
  - `db_port` - MySQL port (default: 3306)
  - `db_user` - MySQL user (default: "admin")
  - `db_password` - MySQL password
  - `db_name` - Database name (default: "loan_approval")

### `api/routes.py`
All endpoints updated to use MySQL database with in-memory fallback:

1. **`POST /api/v1/apply`** - Submit application
   - Saves to `applications` table
   - Maintains in-memory record for backwards compatibility

2. **`GET /api/v1/status/{applicant_id}`** - Get status
   - Reads from `applications` and `decisions` tables
   - Falls back to in-memory store if not found

3. **`GET /api/v1/decision/{applicant_id}`** - Get decision
   - Reads from `decisions` table
   - Falls back to in-memory store if not found

4. **`GET /api/v1/applications`** - List all
   - Queries from `applications` table with pagination
   - Falls back to in-memory store if database is empty

5. **`GET /api/v1/metrics`** - System metrics
   - Counts from `applications` table
   - Falls back to in-memory count on error

6. **`process_application_async()`** - Background processing
   - Saves decision to `decisions` table
   - Updates `applications` table status
   - Maintains in-memory records

### `main.py`
- ✅ Imported database initialization functions
- ✅ Added startup event to create database tables
  - Automatically creates schema on application startup
  - Gracefully handles missing MySQL (logs warning, continues with in-memory)
- ✅ Added shutdown event to close database connections

## Database Schema

### Applications Table
```
┌─────────────────────┬──────────┬──────────────────────────────────────┐
│ Column              │ Type     │ Notes                                │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ id                  │ INT      │ Primary key, auto-increment          │
│ applicant_id        │ VARCHAR  │ Unique, indexed                      │
│ applicant_name      │ VARCHAR  │ Full name                            │
│ age                 │ INT      │ Applicant age                        │
│ income              │ FLOAT    │ Monthly income                       │
│ employment_type     │ ENUM     │ salaried/self_employed/freelance     │
│ credit_score        │ INT      │ Credit score (300-850)               │
│ loan_amount         │ FLOAT    │ Requested loan amount                │
│ loan_tenure_months  │ INT      │ Loan tenure in months                │
│ existing_liabilities│ FLOAT    │ Existing debts                       │
│ location            │ VARCHAR  │ Applicant location/state             │
│ employment_years    │ FLOAT    │ Years of employment                  │
│ status              │ ENUM     │ processing/approved/rejected/etc.    │
│ risk_score          │ FLOAT    │ Calculated risk score                │
│ error               │ TEXT     │ Error message if processing failed   │
│ created_at          │ DATETIME │ Indexed                              │
│ updated_at          │ DATETIME │ Updated on any change                │
└─────────────────────┴──────────┴──────────────────────────────────────┘
```

### Decisions Table
```
┌──────────────────────────┬────────┬────────────────────────────────────┐
│ Column                   │ Type   │ Notes                              │
├──────────────────────────┼────────┼────────────────────────────────────┤
│ id                       │ INT    │ Primary key, auto-increment        │
│ applicant_id             │ VARCHAR│ Unique, indexed                    │
│ application_status       │ VARCHAR│ approved/rejected/manual_review    │
│ risk_score               │ FLOAT  │ Final risk score                   │
│ confidence_level         │ FLOAT  │ Decision confidence (0-100)        │
│ applicant_profile        │ JSON   │ Full agent output (JSON)           │
│ financial_risk           │ JSON   │ Risk analysis output (JSON)        │
│ loan_decision            │ JSON   │ Decision output (JSON)             │
│ compliance_action        │ JSON   │ Compliance action (JSON)           │
│ final_explanation        │ TEXT   │ Human-readable explanation         │
│ next_steps               │ JSON   │ Next steps array (JSON)            │
│ processing_duration_secs │ FLOAT  │ Time to process in seconds         │
│ processing_timestamp     │ DATETIME│ When processing completed         │
│ created_at               │ DATETIME│ Indexed                           │
└──────────────────────────┴────────┴────────────────────────────────────┘
```

## Configuration

Update `.env` file with MySQL credentials:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=password
DB_NAME=loan_approval
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up MySQL

**Option A: Local Installation**
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

**Option B: Docker (Recommended)**
```bash
docker run --name loan-approval-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=loan_approval \
  -e MYSQL_USER=admin \
  -e MYSQL_PASSWORD=password \
  -p 3306:3306 \
  -d mysql:8.0
```

### 3. Create Database User (if not using Docker)
```sql
CREATE DATABASE loan_approval;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON loan_approval.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Run Application
```bash
python main.py
```

The application will automatically create all database tables on startup.

## Backwards Compatibility

The system maintains full backwards compatibility:

- **In-memory fallback**: If MySQL is unavailable, the system continues to work using in-memory storage
- **Dual writes**: All data is written to both database and in-memory store during transition
- **Read priority**: Database is read first, then in-memory as fallback
- **Graceful degradation**: No breaking changes to API or behavior

## Verification

### Check Database Creation
```bash
mysql -u admin -p loan_approval -e "SHOW TABLES;"
```

Should output:
```
+------------------------+
| Tables_in_loan_approval|
+------------------------+
| applications           |
| decisions              |
+------------------------+
```

### Submit Test Application
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

### Verify Data in Database
```bash
mysql -u admin -p loan_approval -e "SELECT * FROM applications;"
```

## Performance Characteristics

- **Connection Pooling**: Default 5 connections with 10 overflow
- **Query Optimization**: Indexed on `applicant_id` and `created_at`
- **Pool Recycling**: Connections recycled every 1 hour
- **Pre-ping**: All connections tested before use

## What's Next

### Optional Enhancements
1. Set up Alembic for schema migrations
2. Configure replication for high availability
3. Add query caching layer
4. Set up automated backups
5. Monitor slow queries and optimize

### For Production
1. Use strong database passwords
2. Enable SSL/TLS for database connections
3. Set up regular backups
4. Configure monitoring and alerting
5. Use read replicas for scaling

## Files Reference

| File | Purpose |
|------|---------|
| `src/db/models.py` | SQLAlchemy ORM models |
| `src/db/database.py` | Connection management |
| `src/db/repository.py` | Data access layer |
| `src/config.py` | Configuration (updated) |
| `api/routes.py` | API endpoints (updated) |
| `main.py` | Application startup (updated) |
| `requirements.txt` | Dependencies (updated) |
| `DATABASE_SETUP.md` | Detailed setup guide |

## Testing

Run the full test suite:
```bash
pytest tests/ -v
```

To test database operations specifically:
```bash
pytest tests/test_orchestrator.py -v -k database
```

## Support

See `DATABASE_SETUP.md` for:
- Detailed troubleshooting
- Database queries and monitoring
- Backup and recovery procedures
- Performance optimization tips
