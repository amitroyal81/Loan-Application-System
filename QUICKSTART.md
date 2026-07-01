# Quick Start Guide

## 1. Installation (5 minutes)

### Step 1: Set up environment
```bash
cd /home/ubuntu/loan-approval-system

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API key
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
# Example:
# ANTHROPIC_API_KEY=sk-ant-...
```

## 2. Run the System (3 terminals)

### Terminal 1: Start FastAPI Server
```bash
python main.py
```
Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Streamlit UI
```bash
cd ui
streamlit run app.py
```
Expected output:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Terminal 3: Verify system (optional)
```bash
# Test API health
curl http://localhost:8000/api/v1/health

# Should return:
# {"status": "healthy", "timestamp": "...", ...}
```

## 3. Test the System

### Via Streamlit UI
1. Open browser to `http://localhost:8501`
2. Go to "🆕 New Application"
3. Fill in sample data:
   - Name: John Doe
   - Age: 35
   - Monthly Income: $5,000
   - Credit Score: 720
   - Loan Amount: $50,000
   - Loan Tenure: 60 months
   - Employment: Salaried
4. Click "📨 Submit Application"
5. Click "📋 Check Status" to view decision

### Via API (curl)
```bash
# 1. Submit application
curl -X POST http://localhost:8000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
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

# 2. Wait 2-3 seconds, then check status
curl http://localhost:8000/api/v1/status/TEST001

# 3. Get full decision
curl http://localhost:8000/api/v1/decision/TEST001
```

## 4. View System Metrics

### Via Streamlit
- Go to "📈 Metrics" tab to see system statistics

### Via API
```bash
curl http://localhost:8000/api/v1/metrics
```

## 5. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v

# Run with coverage
pytest tests/ --cov=src -v
```

## 6. Key Files for Evaluation

### Architecture & Design
- `CLAUDE.md` - Complete architecture documentation
- `src/orchestrator.py` - LangGraph state machine orchestration
- `src/agents/` - Individual agent implementations

### API & Microservice
- `main.py` - FastAPI application entry point
- `api/routes.py` - REST API endpoints

### User Interface
- `ui/app.py` - Streamlit chatbot UI

### Testing
- `tests/test_agents.py` - Agent unit tests
- `tests/test_orchestrator.py` - Orchestration tests

## 7. Project Structure Overview

```
loan-approval-system/
├── src/                      # Main source code
│   ├── agents/              # Domain-specific agents
│   ├── mcp_servers/         # MCP server implementations
│   ├── models/              # Pydantic schemas
│   ├── utils/               # Utility functions
│   ├── orchestrator.py      # LangGraph orchestrator ⭐
│   └── config.py            # Configuration
├── api/                     # FastAPI routes
├── ui/                      # Streamlit UI
├── tests/                   # Unit & integration tests
├── main.py                  # FastAPI entry point ⭐
├── requirements.txt         # Dependencies
├── README.md                # Full documentation
├── CLAUDE.md               # Architecture docs ⭐
├── QUICKSTART.md           # This file
└── .env.example            # Environment template
```

## 8. Troubleshooting

### Issue: "Connection refused" in Streamlit
**Solution**: Ensure FastAPI server is running in Terminal 1

### Issue: "ANTHROPIC_API_KEY not set"
**Solution**: 
1. Check `.env` file has correct API key
2. Restart FastAPI server after updating .env

### Issue: "Port 8000 already in use"
**Solution**: Change port in `.env`:
```
API_PORT=8001
```

### Issue: "ModuleNotFoundError"
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## 9. Next Steps

1. **Live Code Walkthrough**
   - Review `CLAUDE.md` for architecture
   - Walk through `src/orchestrator.py` to understand state machine
   - Examine each agent implementation

2. **Modify and Test**
   - Change risk thresholds in `src/mcp_servers/risk_rules_db.py`
   - Add new decision rules in `src/mcp_servers/decision_synthesis.py`
   - Test changes by submitting new applications

3. **Production Deployment**
   - Replace in-memory storage with database
   - Add authentication to API
   - Configure monitoring and logging
   - Deploy with Docker/Kubernetes

4. **Advanced Features**
   - Connect real credit bureaus via MCP
   - Implement document processing
   - Add explainability dashboard
   - Create admin approval workflows

## 10. System Architecture Summary

```
User (Streamlit) 
    ↓ HTTP
FastAPI (http://localhost:8000)
    ↓ 
LangGraph Orchestrator
    ↓
4 Domain-Specific Agents
    ├→ ApplicantProfileAgent (credit history, employment)
    ├→ FinancialRiskAgent (DTI, anomalies)
    ├→ LoanDecisionAgent (Approve/Reject/Review)
    └→ ComplianceActionAgent (notifications, audit)
    ↓
MCP Servers (domain context)
    ├→ ApplicantDB
    ├→ RiskRulesDB
    ├→ DecisionSynthesis
    └→ NotificationSystem
    ↓
Claude Sonnet 4.6 LLM
```

## 11. Demo Application Data

**Approved Case** (Low Risk):
```json
{
  "age": 35,
  "income": 8000,
  "employment_type": "salaried",
  "credit_score": 760,
  "loan_amount": 40000,
  "employment_years": 8,
  "existing_liabilities": 5000
}
```

**Rejected Case** (High Risk):
```json
{
  "age": 25,
  "income": 2000,
  "employment_type": "freelance",
  "credit_score": 580,
  "loan_amount": 100000,
  "employment_years": 0.5,
  "existing_liabilities": 50000
}
```

**Manual Review Case** (Marginal):
```json
{
  "age": 40,
  "income": 5000,
  "employment_type": "self_employed",
  "credit_score": 650,
  "loan_amount": 50000,
  "employment_years": 3,
  "existing_liabilities": 25000
}
```

---

**Ready to evaluate!** 🚀 Follow steps 1-3 to get running in under 10 minutes.
