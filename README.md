# Agentic AI Intelligent Loan Approval System

A production-grade Multi-Agent Agentic AI system for automated loan approval with explainability, auditability, and scalability.

## 🏗️ Architecture Overview

```
Streamlit UI (Presentation Layer)
    ↓
FastAPI (Microservice Layer)
    ↓
LangGraph Orchestrator (Orchestration Layer)
    ↓
MCP Servers (Communication Layer)
    ↓
Domain-Specific Agents + Claude Sonnet 4.6 (Agent Layer)
```

## 📋 Key Components

### 1. **Presentation Layer** - Streamlit UI (`ui/app.py`)
- User-friendly chatbot interface for loan applications
- Real-time status tracking
- Decision visualization and explanations
- Metrics dashboard

### 2. **Microservice Layer** - FastAPI (`main.py`, `api/routes.py`)
- REST API endpoints for loan application submission
- Application status tracking
- Health checks and metrics

### 3. **Orchestration Layer** - LangGraph (`src/orchestrator.py`)
- State machine-based workflow management
- Coordinates all agents in sequence
- Handles error recovery and fallback logic
- Audit trail and workflow history

### 4. **Agent Layer** - Specialized Agents (`src/agents/`)

#### 4.1 Applicant Profile Agent
- Analyzes applicant profile and history
- Calculates income stability score
- Determines employment risk level
- Provides credit history summary
- **MCP Server**: ApplicantDB

#### 4.2 Financial Risk Analysis Agent
- Calculates debt-to-income ratio
- Assesses credit score risk
- Evaluates loan amount risk
- Detects anomalies in application data
- **MCP Server**: RiskRulesDB

#### 4.3 Loan Decision Agent
- Synthesizes decisions from other agents
- Classifies as Approved/Rejected/Manual Review
- Calculates confidence level
- Extracts key decision factors
- **MCP Server**: DecisionSynthesis

#### 4.4 Compliance & Action Orchestrator Agent
- Creates case records for tracking
- Sends notifications to applicants
- Logs actions and decisions
- Generates compliance reports
- **MCP Server**: NotificationSystem

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip or conda
- API Key for Anthropic Claude (set in `.env`)

### Installation

1. **Clone and navigate to project**
```bash
cd /home/ubuntu/loan-approval-system
```

2. **Create virtual environment** (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the System

#### Terminal 1: Start FastAPI Server
```bash
python main.py
```
The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

#### Terminal 2: Start Streamlit UI
```bash
cd ui
streamlit run app.py
```
The UI will be available at `http://localhost:8501`

## 📊 System Workflow

### Complete Processing Flow

1. **User Submission**
   - User submits loan application via Streamlit chatbot
   - Form validation on client side

2. **API Ingestion**
   - FastAPI receives application
   - Stores application record with status "processing"
   - Returns acknowledgment with case ID

3. **Orchestrator Routing**
   - LangGraph orchestrator initiates workflow
   - Application data passed through agent pipeline

4. **Agent Execution (Sequential)**
   ```
   Applicant Profile Analysis
        ↓
   Financial Risk Analysis
        ↓
   Loan Decision Synthesis
        ↓
   Compliance & Actions
   ```

5. **Decision Synthesis**
   - All agent outputs combined
   - Risk scores and confidence calculated
   - Final classification determined

6. **Response & Notification**
   - Decision stored with full audit trail
   - Applicant notified via email/SMS
   - Case marked as complete

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v
```

### Test with Sample Application

```bash
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
```

Check status:
```bash
curl http://localhost:8000/api/v1/status/TEST001
```

## 📁 Project Structure

```
loan-approval-system/
├── src/
│   ├── agents/
│   │   ├── base_agent.py          # Base agent class
│   │   ├── applicant_agent.py     # Applicant profile analysis
│   │   ├── risk_agent.py          # Financial risk analysis
│   │   ├── decision_agent.py      # Decision synthesis
│   │   └── compliance_agent.py    # Compliance & actions
│   ├── mcp_servers/
│   │   ├── applicant_db.py        # Applicant database MCP
│   │   ├── risk_rules_db.py       # Risk rules MCP
│   │   ├── decision_synthesis.py  # Decision synthesis MCP
│   │   └── notification_system.py # Notification MCP
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── config.py                  # Configuration management
│   ├── orchestrator.py            # LangGraph orchestrator
│   └── utils/
│       └── validators.py          # Input validation
├── api/
│   └── routes.py                  # FastAPI routes
├── ui/
│   └── app.py                     # Streamlit UI
├── tests/
│   ├── test_agents.py             # Agent tests
│   └── test_orchestrator.py       # Orchestrator tests
├── main.py                        # FastAPI entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## 🔑 Key Features

### 1. **Multi-Agent Architecture**
- Independent agents with clear responsibilities
- Loose coupling through message passing
- Scalable and maintainable design

### 2. **LangGraph Orchestration**
- State machine-based workflow
- Deterministic execution flow
- Audit trail and history tracking

### 3. **MCP (Model Context Protocol)**
- Standardized agent communication
- Domain-specific context servers
- Extensible architecture

### 4. **Explainable AI**
- Each agent provides reasoning
- Key decision factors highlighted
- Full decision audit trail

### 5. **Risk-Based Classification**
- Automated risk scoring
- Three-tier decision system (Approve/Reject/Review)
- Confidence-based routing

## 📊 API Endpoints

### Loan Application
- **POST** `/api/v1/apply` - Submit new loan application
- **GET** `/api/v1/status/{applicant_id}` - Get application status
- **GET** `/api/v1/decision/{applicant_id}` - Get final decision

### System
- **GET** `/api/v1/health` - Health check
- **GET** `/api/v1/metrics` - System metrics
- **GET** `/api/v1/applications` - List all applications

## 🔐 Security Considerations

1. **Input Validation** - All inputs validated against schema
2. **Error Handling** - Safe error messages without data exposure
3. **Audit Trail** - All decisions logged with timestamp and user
4. **API Security** - CORS configured, authentication ready

## 📈 Performance

- Average processing time per application: 2-5 seconds
- Supports concurrent application processing
- Scalable to hundreds of concurrent users

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **UI** | Streamlit |
| **API** | FastAPI |
| **Orchestration** | LangGraph, LangChain |
| **LLM** | Anthropic Claude Sonnet 4.6 |
| **MCP Framework** | FastMCP |
| **Agent SDK** | Anthropic Agent SDK |
| **Validation** | Pydantic |
| **Testing** | pytest, pytest-asyncio |

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests: `pytest tests/ -v`
4. Submit pull request

## 📝 License

This project is provided as-is for evaluation and educational purposes.

## 📞 Support

For issues or questions:
- Check the API documentation at `/docs`
- Review logs in application console
- Test endpoints using provided curl examples

---

**Built with ❤️ using Agentic AI and Claude**
