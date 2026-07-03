# MySQL Database Setup Guide

This guide explains how to set up and configure the MySQL database for the Agentic AI Loan Approval System.

## Overview

The system has been migrated from in-memory Python dictionaries to MySQL for persistent data storage. The implementation includes:

- **SQLAlchemy ORM** for database abstraction
- **Repository Pattern** for clean data access
- **Backwards compatibility** with in-memory fallback
- **Two database tables**: `applications` and `decisions`

## Prerequisites

- MySQL 5.7+ or MySQL 8.0+
- Python 3.8+
- All Python dependencies installed: `pip install -r requirements.txt`

## Installation

### 1. Install MySQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

**macOS (with Homebrew):**
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

**Windows:**
- Download from https://dev.mysql.com/downloads/mysql/
- Run the installer

**Using Docker (Recommended for Development):**
```bash
docker run --name loan-approval-mysql \
  -e MYSQL_ROOT_PASSWORD=Tek@12345 \
  -e MYSQL_DATABASE=loan_approval \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=password \
  -p 3306:3306 \
  -d mysql:8.0
```

### 2. Create Database and User

If not using Docker, connect to MySQL and run:

```sql
CREATE DATABASE IF NOT EXISTS loan_approval;
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON loan_approval.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Environment Variables

Update your `.env` file with database credentials:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=password
DB_NAME=loan_approval
```

For Docker setup:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=password
DB_NAME=loan_approval
```

### 4. Verify Database Connection

Test the connection by running the application. It will create tables automatically on startup:

```bash
python main.py
```

You should see in the logs:
```
Initializing database: localhost:3306/loan_approval
Database initialized successfully
```

## Database Schema

### applications Table

Stores all loan applications:

```sql
CREATE TABLE applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id VARCHAR(255) UNIQUE NOT NULL,
    applicant_name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    income FLOAT NOT NULL,
    employment_type ENUM('salaried', 'self_employed', 'freelance', 'unemployed') NOT NULL,
    credit_score INT NOT NULL,
    loan_amount FLOAT NOT NULL,
    loan_tenure_months INT NOT NULL,
    existing_liabilities FLOAT DEFAULT 0,
    location VARCHAR(255) NOT NULL,
    employment_years FLOAT NOT NULL,
    status ENUM('processing', 'approved', 'rejected', 'manual_review', 'failed', 'completed') DEFAULT 'processing',
    risk_score FLOAT,
    error TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_created_at (created_at)
);
```

### decisions Table

Stores final loan decisions and detailed analysis:

```sql
CREATE TABLE decisions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    applicant_id VARCHAR(255) UNIQUE NOT NULL,
    application_status VARCHAR(50) NOT NULL,
    risk_score FLOAT NOT NULL,
    confidence_level FLOAT NOT NULL,
    applicant_profile JSON,
    financial_risk JSON,
    loan_decision JSON,
    compliance_action JSON,
    final_explanation TEXT,
    next_steps JSON,
    processing_duration_seconds FLOAT,
    processing_timestamp DATETIME,
    created_at DATETIME NOT NULL,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_created_at (created_at)
);
```

## API Usage

### Submit Loan Application

The API now persists data to MySQL:

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

Data is stored in the `applications` table.

### Check Application Status

```bash
curl http://localhost:8000/api/v1/status/APP001
```

Returns application status and decision from MySQL.

### Get Loan Decision

```bash
curl http://localhost:8000/api/v1/decision/APP001
```

Returns detailed decision from the `decisions` table.

### List All Applications

```bash
curl http://localhost:8000/api/v1/applications
```

Returns all applications from MySQL with pagination.

## Querying the Database

Connect to MySQL directly to inspect data:

```bash
mysql -u admin -p loan_approval
```

### Useful Queries

View all applications:
```sql
SELECT applicant_id, status, risk_score, created_at FROM applications ORDER BY created_at DESC;
```

View all decisions:
```sql
SELECT applicant_id, application_status, confidence_level FROM decisions;
```

View specific applicant:
```sql
SELECT * FROM applications WHERE applicant_id = 'APP001';
SELECT * FROM decisions WHERE applicant_id = 'APP001';
```

Count statistics:
```sql
SELECT 
    COUNT(*) as total_applications,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
    SUM(CASE WHEN status = 'manual_review' THEN 1 ELSE 0 END) as manual_review
FROM applications;
```

## Backwards Compatibility

The system maintains backwards compatibility with the original in-memory storage:

- **Read Priority**: Database first, then in-memory fallback
- **Write Both**: Applications write to both database and in-memory store
- **Graceful Degradation**: If database is unavailable, the system falls back to in-memory storage

This means:
1. If MySQL is not available, the system still works with in-memory storage
2. Data is lost when the app restarts (unless MySQL is configured)
3. Multiple instances cannot share state without MySQL

## Connection Pooling

The system uses SQLAlchemy's built-in connection pooling:

- **Pool Size**: Default 5 connections
- **Max Overflow**: Default 10 additional connections
- **Pool Recycle**: 3600 seconds (1 hour)
- **Pool Pre-Ping**: Enabled (tests connection before use)

For production, adjust in `src/db/database.py`:

```python
engine = create_engine(
    db_url,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600
)
```

## Troubleshooting

### Error: "Connection refused"

**Cause**: MySQL server is not running or credentials are wrong

**Solution**:
1. Check MySQL is running: `systemctl status mysql` (Linux) or `brew services list` (Mac)
2. Verify credentials in `.env` file
3. Test connection: `mysql -u admin -p loan_approval`

### Error: "Unknown database 'loan_approval'"

**Cause**: Database was not created

**Solution**:
```sql
CREATE DATABASE loan_approval;
```

### Error: "Access denied for user 'admin'@'localhost'"

**Cause**: Password is incorrect or user doesn't exist

**Solution**:
```sql
ALTER USER 'admin'@'localhost' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

### Data not persisting after restart

**Cause**: Not using MySQL (falling back to in-memory storage)

**Solution**:
1. Check logs for "Database initialized successfully"
2. Verify MySQL credentials in `.env`
3. Test manual connection: `mysql -u admin -p loan_approval`

## Performance Optimization

### For Production

1. **Create Indexes**: The system automatically creates indexes on:
   - `applicant_id` (for quick lookups)
   - `created_at` (for sorting and time-based queries)

2. **Optimize Queries**:
   - Use pagination for `/api/v1/applications`
   - Consider caching for frequently accessed decisions

3. **Monitor Connections**:
   ```sql
   SHOW PROCESSLIST;
   ```

4. **Enable Query Logging** (if needed):
   ```sql
   SET GLOBAL slow_query_log = 'ON';
   SET GLOBAL long_query_time = 2;
   ```

## Backup and Recovery

### Backup Database

```bash
# Full backup
mysqldump -u admin -p loan_approval > backup_$(date +%Y%m%d).sql

# With Docker
docker exec loan-approval-mysql mysqldump -u admin -padmin loan_approval > backup.sql
```

### Restore from Backup

```bash
mysql -u admin -p loan_approval < backup_20240101.sql
```

## Migration from In-Memory to MySQL

All new applications automatically use MySQL. Existing in-memory data will:

1. Continue to work if MySQL is unavailable
2. Be stored in both places until MySQL is available
3. Migrate to MySQL-only on restart once MySQL is configured

## Future Enhancements

Consider these improvements:

1. **Alembic Migrations** - Schema versioning and rollbacks
2. **Read Replicas** - Distribute read load
3. **Replication** - High availability with master-slave setup
4. **Sharding** - Horizontal scaling for large datasets
5. **Archive Tables** - Move old decisions to archive for performance
6. **Audit Triggers** - Automatic change tracking

## Support

For issues or questions:

1. Check logs: Application logs show database initialization status
2. Verify MySQL: `mysql -u admin -p -e "SELECT 1;"`
3. Test connection: Check DB_* variables in `.env`
4. Review errors in application startup output
