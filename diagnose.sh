#!/bin/bash

# Diagnostic script to check database saving issues

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       LOAN APPROVAL SYSTEM - DATABASE DIAGNOSIS                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "[1/6] Checking MySQL Connection..."
mysql -h localhost -u root -pTek@12345 -e "SELECT 1;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ MySQL is running and accessible"
else
    echo "✗ MySQL connection failed"
    echo "  Solution: sudo systemctl start mysql"
    exit 1
fi

echo ""
echo "[2/6] Checking Database Exists..."
DB_EXISTS=$(mysql -h localhost -u root -pTek@12345 -e "SHOW DATABASES LIKE 'loan_approval';" 2>/dev/null | grep loan_approval)
if [ ! -z "$DB_EXISTS" ]; then
    echo "✓ Database 'loan_approval' exists"
else
    echo "✗ Database 'loan_approval' not found"
    echo "  Solution: Run 'python main.py' to create it"
    exit 1
fi

echo ""
echo "[3/6] Checking Tables Exist..."
TABLES=$(mysql -h localhost -u root -pTek@12345 loan_approval -e "SHOW TABLES;" 2>/dev/null | wc -l)
if [ $TABLES -ge 2 ]; then
    echo "✓ Tables found"
    mysql -h localhost -u root -pTek@12345 loan_approval -e "SHOW TABLES;" 2>/dev/null
else
    echo "✗ No tables found"
    echo "  Solution: Run 'python main.py' to create tables"
    exit 1
fi

echo ""
echo "[4/6] Checking Application Count..."
APP_COUNT=$(mysql -h localhost -u root -pTek@12345 loan_approval -e "SELECT COUNT(*) FROM applications;" 2>/dev/null | tail -1)
echo "✓ Applications in database: $APP_COUNT"

echo ""
echo "[5/6] Recent Applications..."
mysql -h localhost -u root -pTek@12345 loan_approval -e "SELECT applicant_id, status, created_at FROM applications ORDER BY created_at DESC LIMIT 5;" 2>/dev/null

echo ""
echo "[6/6] Environment Configuration..."
echo "Database Configuration from .env:"
grep "^DB_" /home/ubuntu/loan-approval-system/.env

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DIAGNOSIS COMPLETE                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "Quick Test: Run the following to test data saving:"
echo ""
echo "1. Terminal 1: python main.py"
echo ""
echo "2. Terminal 2:"
echo "   curl -X POST http://localhost:8000/api/v1/apply \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"applicant_id\":\"TEST_$(date +%s)\",\"applicant_name\":\"Test\",\"age\":35,...}'"
echo ""
echo "3. Terminal 2:"
echo "   ./query_db.sh 1"
echo ""
