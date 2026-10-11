# Personal Finance AI Advisor — Monorepo

An AI-driven Personal Finance Advisor monorepo delivering real-time precious metals spot market data (Gold & Silver in INR), grounded GST and financial education document retrieval via Chroma RAG, and conversational agent orchestration powered by Google Gemini.

---

## 1. Monorepo Architecture

This repository is structured as a decoupled monorepo designed for independent backend and frontend lifecycles, local development, and distinct cloud deployments:

* **Backend Service (`backend/`):** High-reliability FastAPI REST API with Chroma vector retrieval, Gold-API spot pricing, and Gemini tool orchestration. Deployed on **Render** (or Docker).
* **Frontend Application (`frontend/`):** Reserved workspace for the upcoming Next.js / TypeScript web application. Deployed on **Vercel**.
* **Original Research Notebook (`financeadvisor.ipynb`):** The foundational Google Colab prototype preserved untouched at the repository root.

```
financeadvisor/
│
├── backend/                           # Production FastAPI Backend Service
│   ├── app/                           # Application source code
│   │   ├── main.py                    # FastAPI entrypoint
│   │   ├── api/                       # API router & versioned routes
│   │   ├── core/                      # Configuration, logging, exception hierarchy
│   │   ├── schemas/                   # Pydantic v2 validation models
│   │   ├── services/                  # Business logic (Market data, RAG, Agent)
│   │   ├── repositories/              # Persistent Chroma repository
│   │   └── utils/                     # Math & Decimal unit conversions
│   │
│   ├── tests/                         # Comprehensive automated test suite
│   │   ├── unit/                      # Math, Settings, and Service tests
│   │   ├── contract/                  # FastAPI HTTP endpoint contract tests
│   │   ├── integration/               # Real network & vector store integration tests
│   │   ├── test_agent_tools.py        # Notebook & tool tests
│   │   ├── test_static_and_security.py # Static code & secret tests
│   │   └── run_all.py                 # Master test suite runner
│   │
│   ├── data/
│   │   └── pdfs/                      # Cached SEBI & CBIC reference documents (gitignored)
│   │
│   ├── chroma_langchain_db/           # Persistent Chroma vector store (504 chunks, gitignored)
│   │
│   ├── audit/                         # Phase 1 forensic audit logs and reports
│   │
│   ├── .env                           # Local environment secrets (gitignored)
│   ├── .env.example                   # Environment configuration template
│   ├── .gitignore                     # Backend-specific exclusions
│   ├── requirements.txt               # Python production dependencies
│   ├── pytest.ini                     # Pytest runner configuration
│   ├── Dockerfile                     # Production container definition
│   └── README.md                      # Backend operations guide & Render deployment
│
├── frontend/                          # Future Next.js Frontend Workspace
│   └── README.md                      # Frontend architecture & Vercel deployment spec
│
├── financeadvisor.ipynb               # Original Google Colab notebook (preserved)
├── .gitignore                         # Monorepo root Git exclusions
└── README.md                          # Monorepo master documentation
```

---

## 2. Component Links & Documentation

* **Backend Guide & API Spec:** [backend/README.md](file:///c:/Users/chara/OneDrive/Desktop/projects/finance%20agent/financeadvisor/backend/README.md)
* **Frontend Workspace Spec:** [frontend/README.md](file:///c:/Users/chara/OneDrive/Desktop/projects/finance%20agent/financeadvisor/frontend/README.md)
* **Original Google Colab Notebook:** [financeadvisor.ipynb](file:///c:/Users/chara/OneDrive/Desktop/projects/finance%20agent/financeadvisor/financeadvisor.ipynb)

---

## 3. Quick Start (Local Backend Development)

The backend service can be operated either from the repository root or directly from the `backend/` directory.

### Quick Commands (from Repository Root)

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # Linux / macOS

# 2. Configure environment
Copy-Item backend\.env.example backend\.env

# 3. Start the FastAPI development server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# 4. Run the full test suite
python backend/tests/run_all.py
```

### Quick Commands (from `backend/` Directory)

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pytest tests -v
```

* **Interactive API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 4. Deployment Strategy

| Component | Target Platform | Root Directory | Build Command | Start Command |
|---|---|---|---|---|
| **Backend** | Render (Web Service) | `backend` | `pip install -r requirements.txt` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Frontend** | Vercel | `frontend` | *(Configured in frontend phase)* | *(Configured in frontend phase)* |

---

## 5. Security & Secret Protection

> [!CAUTION]
> **NEVER commit `.env` files or API credentials to version control.**
>
> 1. Both `.env` and `backend/.env` are strictly excluded by `.gitignore`.
> 2. `GEMINI_API_KEY` is a confidential server-side credential and must **NEVER** be prefixed with `NEXT_PUBLIC_` or shared with the frontend.
> 3. Vector database files (`chroma_langchain_db/`) and downloaded reference PDFs (`data/pdfs/`) are local runtime assets and are gitignored to prevent bloated commits.