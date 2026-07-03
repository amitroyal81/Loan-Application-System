# Implementation Details: MySQL Database Integration

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     Application Layer                         │
│         (Streamlit UI + FastAPI REST API)                    │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                   API Routes Layer                            │
│              (api/routes.py - Updated)                       │
│  ├─ submit_loan_application()                               │
│  ├─ get_application_status()                                │
│  ├─ get_loan_decision()                                     │
│  └─ process_application_async()                             │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                 Repository Pattern Layer                      │
│            (src/db/repository.py - NEW)                      │
│  ├─ LoanApplicationRepository                               │
│  │  ├─ create_application()                                │
│  │  ├─ get_application()                                   │
│  │  ├─ update_application_status()                         │
│  │  ├─ update_application_decision()                       │
│  │  ├─ list_all_applications()                             │
│  │  └─ get_applications_count()                            │
│  │                                                           │
│  └─ LoanDecisionRepository                                  │
│     ├─ create_decision()                                    │
│     ├─ get_decision()                                       │
│     └─ decision_exists()                                    │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────────────┐
│              SQLAlchemy ORM Layer                            │
│         (src/db/models.py + src/db/database.py)             │
│  ├─ LoanApplicationModel                                    │
│  ├─ LoanDecisionModel                                       │
│  └─ Connection Management                                  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                  MySQL Database                              │
│  ├─ applications table                                       │
│  └─ decisions table                                          │
└──────────────────────────────────────────────────────────────┘
```

## File Changes

### New Files Created

#### 1. `src/db/__init__.py`
```python
"""Database module for loan approval system"""
```
Purpose: Package initialization marker

#### 2. `src/db/models.py` (NEW)

**LoanApplicationModel** - Maps to `applications` table
```python
class LoanApplicationModel(Base):
    __tablename__ = "applications"
    
    # Fields
    id: int - Primary key
    applicant_id: str - Unique identifier (indexed)
    applicant_name: str
    age: int
    income: float
    employment_type: enum - salaried/self_employed/freelance
    credit_score: int
    loan_amount: float
    loan_tenure_months: int
    existing_liabilities: float
    location: str
    employment_years: float
    
    # Processing fields
    status: enum - processing/approved/rejected/manual_review/failed/completed
    risk_score: float - Calculated risk score
    error: str - Error message if failed
    
    # Timestamps
    created_at: datetime - (indexed)
    updated_at: datetime
```

**LoanDecisionModel** - Maps to `decisions` table
```python
class LoanDecisionModel(Base):
    __tablename__ = "decisions"
    
    # Fields
    id: int - Primary key
    applicant_id: str - Unique identifier (indexed)
    application_status: str
    risk_score: float
    confidence_level: float
    
    # JSON fields for complex data
    applicant_profile: json
    financial_risk: json
    loan_decision: json
    compliance_action: json
    final_explanation: str
    next_steps: json
    
    # Metadata
    processing_duration_seconds: float
    processing_timestamp: datetime
    created_at: datetime - (indexed)
```

#### 3. `src/db/database.py` (NEW)

**Functions:**
- `get_database_url()` - Generates connection string
- `init_db_engine()` - Creates SQLAlchemy engine with connection pooling
  - Pool size: 5 connections
  - Max overflow: 10
  - Pre-ping: Enabled (tests connection before use)
  - Charset: utf8mb4
- `create_db_tables()` - Creates all tables on startup
- `get_db_session()` - Returns new database session
- `close_db_connection()` - Closes all connections

#### 4. `src/db/repository.py` (NEW)

**LoanApplicationRepository:**
```python
class LoanApplicationRepository:
    def __init__(self, db_session: Session)
    
    def create_application(application_data: Dict) → LoanApplicationModel
    def get_application(applicant_id: str) → Optional[LoanApplicationModel]
    def get_application_by_pk(app_id: int) → Optional[LoanApplicationModel]
    def application_exists(applicant_id: str) → bool
    def update_application_status(applicant_id: str, status: str, risk_score: float, error: str)
    def update_application_decision(applicant_id: str, final_decision: Dict)
    def list_all_applications(limit: int, offset: int) → List[LoanApplicationModel]
    def get_applications_count() → int
```

**LoanDecisionRepository:**
```python
class LoanDecisionRepository:
    def __init__(self, db_session: Session)
    
    def create_decision(final_decision: Dict) → LoanDecisionModel
    def get_decision(applicant_id: str) → Optional[LoanDecisionModel]
    def decision_exists(applicant_id: str) → bool
```

### Modified Files

#### 1. `requirements.txt`

**Added:**
```
sqlalchemy==2.0.23
pymysql==1.1.0
alembic==1.13.0
```

**Why:**
- sqlalchemy: ORM framework for database abstraction
- pymysql: Pure Python MySQL driver
- alembic: Migration tool for schema versioning (optional)

#### 2. `src/config.py`

**Added database settings:**
```python
class Settings(BaseSettings):
    # Database
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "admin")
    db_password: str = os.getenv("DB_PASSWORD", "password")
    db_name: str = os.getenv("DB_NAME", "loan_approval")
```

**Benefits:**
- Centralized configuration management
- Environment-based settings (dev/prod/test)
- Secure credential handling

#### 3. `api/routes.py` (MAJOR CHANGES)

**Added imports:**
```python
from src.db.database import get_db_session
from src.db.repository import LoanApplicationRepository, LoanDecisionRepository
```

**Modified functions:**

1. **`submit_loan_application()`**
   - Before: Only saved to `application_store` dict
   - After:
     - Creates database session
     - Creates LoanApplicationRepository
     - Saves to MySQL `applications` table
     - Also saves to `application_store` for backwards compatibility

2. **`get_application_status()`**
   - Before: Looked up `application_store` dict
   - After:
     - Creates database session
     - Queries MySQL `applications` table
     - If found, retrieves related decision from `decisions` table
     - Falls back to `application_store` if not in database

3. **`get_loan_decision()`**
   - Before: Looked up `application_store` dict
   - After:
     - Creates database session
     - Queries MySQL `applications` table
     - Queries MySQL `decisions` table
     - Falls back to `application_store` if not in database

4. **`get_metrics()`**
   - Before: Counted `len(application_store)`
   - After:
     - Creates database session
     - Counts applications from MySQL
     - Falls back to in-memory count on error

5. **`list_applications()`**
   - Before: Iterated `application_store` dict
   - After:
     - Creates database session
     - Queries from MySQL with pagination
     - Falls back to `application_store` if database is empty

6. **`process_application_async()`**
   - Before: Updated `application_store` dict
   - After:
     - Creates database session
     - Calls `repository.update_application_decision()`
     - Creates decision record in `decisions` table
     - Updates `application_store` for backwards compatibility
     - On error: Updates status to "failed" in database and memory

**Pattern in all functions:**
```python
# Create session
db_session = get_db_session()
try:
    # Use repository
    repo = LoanApplicationRepository(db_session)
    result = repo.get_application(applicant_id)
    
    if result:
        return result  # From database
finally:
    db_session.close()

# Fallback to in-memory
if applicant_id in application_store:
    return application_store[applicant_id]
```

#### 4. `main.py` (STARTUP CHANGES)

**Added imports:**
```python
from src.db.database import create_db_tables, close_db_connection
```

**Modified startup event:**
```python
@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    
    # NEW: Initialize database
    try:
        logger.info(f"Initializing database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        create_db_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {str(e)}")
        logger.info("System will use in-memory storage.")
```

**Modified shutdown event:**
```python
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Agentic AI Loan Approval System shutting down")
    
    # NEW: Close database connections
    try:
        close_db_connection()
    except Exception as e:
        logger.warning(f"Error closing database: {str(e)}")
```

## Data Flow

### Application Submission Flow

```
1. User submits application (Streamlit/cURL)
   ↓
2. FastAPI receives POST /api/v1/apply
   ↓
3. API route create session + repository
   ↓
4. Repository.create_application() → Saves to MySQL applications table
   ↓
5. Application store updated (backwards compat)
   ↓
6. Background task queued for processing
```

### Status Check Flow

```
1. User checks status via GET /api/v1/status/APP001
   ↓
2. API route creates session + repository
   ↓
3. Try Repository.get_application() from MySQL
   ├─ If found: Get decision from MySQL decisions table
   └─ If not found: Try application_store
   ↓
4. Return ApplicationStatus object
```

### Decision Processing Flow

```
1. Background task: process_application_async()
   ↓
2. Orchestrator processes application (agents)
   ↓
3. Create session + repository
   ↓
4. Repository.update_application_decision()
   ├─ Update applications table (status)
   └─ Create decisions table record
   ↓
5. Update application_store (backwards compat)
   ↓
6. Status becomes available via GET /api/v1/decision/{id}
```

## Connection Management

### Connection Pool

```
Engine Configuration:
├─ pool_size=5 (max concurrent connections)
├─ max_overflow=10 (temp connections if needed)
├─ pool_pre_ping=True (test connection before use)
├─ pool_recycle=3600 (recycle every 1 hour)
└─ connect_args: charset=utf8mb4

Lifecycle:
├─ Startup: create_db_tables() → creates engine and session
├─ Runtime: get_db_session() → gets connection from pool
├─ Cleanup: db_session.close() → returns to pool
└─ Shutdown: close_db_connection() → closes all connections
```

## Error Handling Strategy

### Database Unavailable

If MySQL connection fails:
1. `create_db_tables()` logs warning
2. Application continues with in-memory storage
3. API endpoints fallback to `application_store`
4. No breaking changes to API contract

### Session Management

Every database operation follows pattern:
```python
db_session = get_db_session()
try:
    # Use repository
    repo = LoanApplicationRepository(db_session)
    # ... operations ...
finally:
    db_session.close()  # Always close
```

### Transaction Handling

All repository methods handle transactions:
- On success: `db_session.commit()`
- On error: `db_session.rollback()` + raise exception

## Backwards Compatibility

### In-Memory Fallback

```
Read Priority:
1. MySQL (try first)
   ├─ Success → return data
   └─ Not found → continue
2. application_store (fallback)
   ├─ Success → return data
   └─ Not found → raise 404

Write Strategy:
├─ Write to MySQL (if available)
├─ Write to application_store (always)
└─ If MySQL fails, use only application_store
```

### Migration Path

```
Day 1 - MySQL Introduced:
├─ New data → Both MySQL + memory
├─ Read → Database first, fallback to memory
└─ Old data still in memory

Day 2 - MySQL Primary:
├─ New queries hit MySQL
├─ Old data migrated via script (optional)
└─ In-memory now just fallback

Day 3+ - Remove In-Memory:
└─ (Only when MySQL is stable)
```

## Performance Characteristics

### Query Performance

```
Single Record Lookup:
├─ MySQL: ~2-5ms (with index)
└─ Memory: ~0.1ms (but lost on restart)

List All (1000 items):
├─ MySQL: ~50-100ms (with pagination)
└─ Memory: ~1-2ms

Insert:
├─ MySQL: ~5-10ms
└─ Memory: ~0.1ms

Update:
├─ MySQL: ~5-10ms
└─ Memory: ~0.1ms
```

### Scalability

```
In-Memory:
├─ Single instance only
├─ Limited by available RAM
└─ No multi-instance support

MySQL:
├─ Multiple instances possible
├─ Read replicas for scaling
├─ Connection pooling enabled
└─ Supports 100+ concurrent requests
```

## Testing Approach

### Unit Tests

Should test repositories directly:
```python
def test_create_application(db_session):
    repo = LoanApplicationRepository(db_session)
    app = repo.create_application(test_data)
    assert app.applicant_id == test_data["applicant_id"]
```

### Integration Tests

Should test with real database:
```python
def test_submit_and_retrieve():
    # Submit via API
    # Check MySQL
    # Check status endpoint
    # Verify data consistency
```

### Fallback Tests

Should test in-memory fallback:
```python
def test_fallback_when_db_unavailable():
    # Disable MySQL connection
    # API should still work
    # Data in memory should be accessible
```

## Deployment Notes

### Development
```bash
docker run --name mysql -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=loan_approval -p 3306:3306 -d mysql:8.0
```

### Production
- Use managed database service (AWS RDS, Azure Database)
- Enable SSL/TLS for connections
- Regular backups
- Monitoring and alerting
- Connection pooling optimization based on load

## Future Enhancements

1. **Alembic Migrations** - Schema versioning
2. **Query Caching** - Redis layer for frequent queries
3. **Read Replicas** - Distribute read load
4. **Archival** - Move old records to archive table
5. **Soft Deletes** - Compliance and audit trail
6. **Audit Triggers** - Track all changes
7. **Full-Text Search** - Search applications by applicant name
8. **Replication** - High availability setup
