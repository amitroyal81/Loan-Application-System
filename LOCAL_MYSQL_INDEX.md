# Local MySQL Setup - Complete Documentation Index

Your Loan Approval System is now **fully configured to use local MySQL** instead of Docker.

## 📋 Quick Summary

| Item | Status |
|------|--------|
| **MySQL Installation** | ✓ Running (localhost:3306) |
| **Database** | ✓ Created (loan_approval) |
| **Tables** | ✓ Created (applications, decisions) |
| **Configuration** | ✓ Updated (.env) |
| **Code** | ✓ Fixed (src/db/database.py) |
| **Data Persistence** | ✓ Working |

---

## 📚 Documentation Files

### For Different Needs:

1. **Quick Start** → Read: `README_LOCAL_MYSQL.md`
   - Fast commands to get started
   - Basic examples
   - Helper script usage

2. **Complete Setup** → Read: `LOCAL_MYSQL_SETUP_COMPLETE.md`
   - Full configuration details
   - Architecture overview
   - All troubleshooting tips

3. **Detailed Setup** → Read: `SETUP_LOCAL_MYSQL.md`
   - Step-by-step guide
   - Schema documentation
   - Testing procedures

4. **SQL Queries** → Read: `MYSQL_QUERIES.sql`
   - 20+ ready-to-use queries
   - Common use cases
   - Paste & run

5. **Verification** → Read: `VERIFICATION.txt`
   - Checklist of all changes
   - Test commands
   - Next steps

---

## 🚀 Quick Commands

```bash
# Start application
python main.py

# Query database easily
./query_db.sh 1      # All applications
./query_db.sh 4      # Approval stats
./query_db.sh 12     # MySQL CLI

# Direct MySQL access
mysql -h localhost -u root -pTek@12345 loan_approval
```

---

## 🔧 Configuration Details

**File**: `.env`
```env
DB_HOST=localhost
DB_PORT=3306          # ← Changed from 5432
DB_USER=root
DB_PASSWORD=Tek@12345
DB_NAME=loan_approval
```

**Modified File**: `src/db/database.py`
- Added URL encoding for password special characters

---

## 📊 Database Schema

### applications Table
- Stores all loan applications
- Fields: applicant_id, name, age, income, credit_score, loan details, status
- Unique index on applicant_id
- Index on created_at for sorting

### decisions Table
- Stores loan decisions and analysis
- Fields: applicant_id, decision, risk_score, confidence, JSON results
- Unique index on applicant_id
- Index on created_at for sorting

---

## 🔗 Data Flow

```
Application Submission
    ↓
FastAPI Endpoint
    ↓
Repository Layer
    ↓
SQLAlchemy ORM
    ↓
Local MySQL Database
    ↓
Persistent Storage ✓
```

All data is queryable at any time via:
- MySQL CLI
- Python API
- SQL queries
- Helper script

---

## ✅ What's Working

- ✓ Application storage in MySQL
- ✓ Decision persistence
- ✓ Data queries via API
- ✓ Direct SQL queries
- ✓ Data survives restarts
- ✓ Helper script for queries
- ✓ Full documentation

---

## 📝 Common Tasks

### View all applications
```bash
./query_db.sh 1
# OR
mysql -h localhost -u root -pTek@12345 loan_approval \
  -e "SELECT * FROM applications;"
```

### View approval statistics
```bash
./query_db.sh 4
```

### Search specific applicant
```bash
./query_db.sh 9 APP001
```

### Connect to MySQL CLI
```bash
./query_db.sh 12
# OR
mysql -h localhost -u root -pTek@12345 loan_approval
```

### Get all decisions
```bash
./query_db.sh 2
```

---

## 🆘 Troubleshooting

**Issue**: MySQL not running
```bash
sudo systemctl start mysql
```

**Issue**: Can't connect
```bash
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;"
```

**Issue**: Database not created
```bash
python main.py  # Auto-creates on startup
```

**Issue**: Tables not found
```bash
mysql -h localhost -u root -pTek@12345 loan_approval -e "SHOW TABLES;"
```

---

## 📁 File Structure

```
loan-approval-system/
├── .env                                    ← Updated
├── src/
│   ├── db/
│   │   ├── database.py                    ← Fixed
│   │   ├── models.py
│   │   └── repository.py
│   └── config.py
├── README_LOCAL_MYSQL.md                  ← Start here
├── LOCAL_MYSQL_SETUP_COMPLETE.md          ← Details
├── SETUP_LOCAL_MYSQL.md                   ← Full guide
├── MYSQL_QUERIES.sql                      ← Query ref
├── query_db.sh                            ← Helper
├── VERIFICATION.txt                       ← Checklist
└── LOCAL_MYSQL_INDEX.md                   ← This file
```

---

## 🎯 Next Steps

1. **Start the app**
   ```bash
   python main.py
   ```

2. **Submit test data**
   ```bash
   curl -X POST http://localhost:8000/api/v1/apply -H "Content-Type: application/json" -d '{...}'
   ```

3. **Query the database**
   ```bash
   ./query_db.sh 3
   ```

4. **Explore more queries**
   - See `MYSQL_QUERIES.sql` for examples
   - Use `query_db.sh` for quick commands

---

## 💾 Data Persistence

✓ **All data is stored in MySQL**
- Applications are saved to database table
- Decisions are saved to database table
- Data survives application restarts
- Multiple app instances can share data
- Full ACID compliance

---

## 🔑 Connection Details

```
Host:              localhost
Port:              3306
Database:          loan_approval
User:              root
Password:          Tek@12345
Python URL:        mysql+pymysql://root:Tek%4012345@localhost:3306/loan_approval
MySQL CLI:         mysql -h localhost -u root -pTek@12345 loan_approval
```

---

## 📖 Documentation Reading Order

1. **First time?** → `README_LOCAL_MYSQL.md`
2. **Want details?** → `LOCAL_MYSQL_SETUP_COMPLETE.md`
3. **Need queries?** → `MYSQL_QUERIES.sql`
4. **Verify setup?** → `VERIFICATION.txt`
5. **Full guide?** → `SETUP_LOCAL_MYSQL.md`

---

## ✨ Features

- ✓ Local MySQL integration
- ✓ URL-encoded passwords (handles special chars)
- ✓ Automatic table creation
- ✓ SQLAlchemy ORM layer
- ✓ Repository pattern
- ✓ Multiple query methods
- ✓ Helper shell script
- ✓ Comprehensive documentation

---

## 🎓 Example Workflow

```bash
# 1. Terminal 1: Start app
python main.py

# 2. Terminal 2: Submit application
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP_123",
    "applicant_name": "Jane Doe",
    "age": 30,
    "income": 6000,
    "employment_type": "salaried",
    "credit_score": 750,
    "loan_amount": 100000,
    "loan_tenure_months": 60,
    "existing_liabilities": 5000,
    "location": "Texas",
    "employment_years": 3
  }'

# 3. Terminal 2: View in database
./query_db.sh 1

# 4. Terminal 2: Get statistics
./query_db.sh 4

# 5. Terminal 2: Query specific applicant
./query_db.sh 9 APP_123
```

---

## 📞 Support Resources

- **Quick answers**: Check `README_LOCAL_MYSQL.md`
- **Detailed answers**: Check `LOCAL_MYSQL_SETUP_COMPLETE.md`
- **Specific queries**: Check `MYSQL_QUERIES.sql`
- **SQL examples**: Run `./query_db.sh` (no args)
- **Direct access**: Use `./query_db.sh 12` or `mysql` CLI

---

**Status**: ✅ **COMPLETE AND READY TO USE**

**Setup Date**: 2026-07-01
**MySQL Version**: 8.0
**Database**: loan_approval
**Tables**: 2
**Data Persistence**: ✅ Active

Start with: `python main.py` then use `./query_db.sh` to explore!
