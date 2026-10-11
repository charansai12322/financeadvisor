# Personal Finance AI Advisor — Backend Service

A modular, production-ready FastAPI backend for the Personal Finance AI Advisor. The service delivers real-time precious metals spot market data (Gold & Silver in INR), grounded GST and financial education document retrieval via Chroma, and Gemini 3.5 Flash agent orchestration.

---

## 1. System Requirements & Architecture

* **Python Version:** Python 3.12.x
* **Framework:** FastAPI with Pydantic v2
* **AI Orchestration:** Google Gemini (`gemini-3.5-flash`) via LangChain / Google GenAI
* **Vector Store:** Chroma (Cosine distance metric, persistent on-disk storage)
* **Market Data:** `api.gold-api.com` (real-time XAU/XAG rates in INR with Decimal precision math)
* **Deployment Target:** Render (Web Service) / Docker

### Directory Layout

```
backend/
├── app/
│   ├── api/
│   │   ├── router.py                  # Aggregated API router
│   │   └── routes/
│   │       ├── health.py              # GET /health
│   │       ├── prices.py              # GET /api/v1/prices/*
│   │       ├── documents.py           # POST /api/v1/documents/search, GET status
│   │       └── advisor.py             # POST /api/v1/advisor/ask
│   ├── core/
│   │   ├── config.py                  # Pydantic Settings with path anchor (BACKEND_DIR)
│   │   ├── logging.py                 # Structured logging with secret redaction
│   │   └── exceptions.py              # Domain exception hierarchy
│   ├── schemas/                       # Typed Pydantic models
│   ├── services/
│   │   ├── market_data.py             # Bullion pricing with Decimal conversion
│   │   ├── document_retrieval.py      # Vector similarity search
│   │   ├── ingest_documents.py        # PDF downloader & idempotent chunk indexer
│   │   ├── gemini.py                  # Gemini model factory
│   │   └── finance_advisor.py         # ReAct agent orchestration
│   ├── repositories/
│   │   └── vector_store.py            # Persistent Chroma repository
│   ├── utils/
│   │   └── price_units.py             # Divisor 31.1035 & unit conversions
│   └── main.py                        # FastAPI application entry point
├── tests/
│   ├── unit/                          # Unit tests (Settings, Math, Services)
│   ├── contract/                      # FastAPI endpoint contract tests
│   ├── integration/                   # Real network integration tests
│   ├── test_agent_tools.py            # Tool calling & agent tests
│   ├── test_static_and_security.py    # Static checks, secrets scan, notebook verification
│   └── run_all.py                     # Master test suite runner
├── data/pdfs/                         # Locally cached reference PDFs (gitignored)
├── chroma_langchain_db/               # Persistent Chroma vector database (gitignored)
├── audit/                             # Phase 1 forensic audit artifacts
├── .env                               # Local secrets (gitignored)
├── .env.example                       # Environment configuration template
├── .gitignore                         # Backend-specific exclusions
├── Dockerfile                         # Production container definition
├── pytest.ini                         # Pytest configuration (pythonpath = .)
└── requirements.txt                   # Production dependencies
```

---

## 2. Local Development Setup

All commands below assume you are working either from the monorepo root or inside the `backend/` directory as indicated.

### Option A: Working from Repository Root (`financeadvisor/`)

#### 1. Create and Activate Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### 3. Configure Environment Variables
```powershell
# Windows PowerShell
Copy-Item backend\.env.example backend\.env

# Linux / macOS
cp backend/.env.example backend/.env
```

#### 4. Run Document Ingestion (Idempotent)
```bash
python -m backend.app.services.ingest_documents
```

#### 5. Start Backend Server
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 6. Run Test Suite
```bash
python backend/tests/run_all.py
```

---

### Option B: Working from Inside `backend/` (`cd backend`)

#### 1. Activate Existing Environment
```powershell
# Windows PowerShell (referencing the root virtual environment)
..\.venv\Scripts\Activate.ps1

# Linux / macOS
source ../.venv/bin/activate
```

#### 2. Configure Environment Variables
```powershell
Copy-Item .env.example .env
```

#### 3. Run Document Ingestion
```bash
python -m app.services.ingest_documents
```

#### 4. Start Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 5. Run Test Suite
```bash
pytest tests -v
# or
python tests/run_all.py
```

---

## 3. Environment Variables Reference

Define these in `backend/.env` for local execution or in your cloud hosting provider dashboard:

| Variable | Type | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | string | `None` | Google AI Studio API Key. If absent, non-AI endpoints continue working. |
| `GEMINI_MODEL` | string | `gemini-3.5-flash` | Gemini model identifier. |
| `GOLD_API_BASE_URL` | string | `https://api.gold-api.com` | Base URL for real-time Gold and Silver spot prices. |
| `APP_ENV` | string | `development` | Environment name (`development` or `production`). |
| `APP_HOST` | string | `127.0.0.1` | Host interface for local Uvicorn binding. |
| `APP_PORT` | integer | `8000` | Port for local server (Render injects `$PORT`). |
| `CORS_ORIGINS` | string | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated allowed frontend origins. |
| `REQUEST_TIMEOUT_SECONDS` | float | `10.0` | Upstream HTTP request timeout. |
| `LOG_LEVEL` | string | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `CHROMA_PERSIST_DIRECTORY` | string | `./chroma_langchain_db` | Path for Chroma storage. Auto-resolves relative to `backend/`. |
| `CHROMA_COLLECTION_NAME` | string | `finance_docs` | Chroma collection name. |
| `PDF_STORAGE_DIR` | string | `./data/pdfs` | Directory for cached PDFs. Auto-resolves relative to `backend/`. |

---

## 4. API Documentation & Endpoints

When the server is running, interactive API documentation is available at:
* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Primary Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck returning `{"status": "ok", "service": "finance-advisor"}` |
| `GET` | `/api/v1/prices/gold` | Live spot Gold rate (INR/gram, INR/10g, INR/troy oz) |
| `GET` | `/api/v1/prices/silver` | Live spot Silver rate (INR/gram, INR/10g, INR/troy oz) |
| `GET` | `/api/v1/prices/{asset}` | Spot rate by asset alias (`gold`, `xau`, `silver`, `xag`) |
| `POST` | `/api/v1/documents/search` | Semantic vector search across GST and SEBI booklets |
| `GET` | `/api/v1/documents/status` | Indexing status, chunk count (504 chunks), and source documents |
| `POST` | `/api/v1/advisor/ask` | ReAct agent orchestration with citations and live market tools |

---

## 5. Render Deployment Configuration

To deploy this backend as a Web Service on **Render**:

1. **Service Type:** Web Service
2. **Repository:** Your GitHub repository
3. **Branch:** `main` (or your deployment branch)
4. **Root Directory:** `backend` *(CRITICAL: Must be set to `backend`)*
5. **Runtime:** Python 3
6. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
7. **Start Command:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
8. **Health Check Path:** `/health`
9. **Environment Variables on Render:**
   * `GEMINI_API_KEY`: Your production Google AI Studio key
   * `GEMINI_MODEL`: `gemini-3.5-flash`
   * `APP_ENV`: `production`
   * `CORS_ORIGINS`: `https://your-frontend-app.vercel.app`
   * `LOG_LEVEL`: `INFO`
10. **Vector Store Persistence Note:**
    * In standard Render free/starter tiers, filesystem writes are ephemeral.
    * For persistent vector search in production, either:
      * Attach a **Render Persistent Disk** mounted at `/app/chroma_langchain_db` and pre-run ingestion during container build, or
      * Set `CHROMA_PERSIST_DIRECTORY` to the persistent disk mount path.
    * If no disk is attached, the backend boots cleanly and endpoints `/health` and `/api/v1/prices/*` operate fully; document search returns indexed status if data was pre-bundled or re-ingested on boot.

---

## 6. Docker Deployment

A production-ready `Dockerfile` is included in this directory.

### Build and Run Locally:
```bash
cd backend
docker build -t finance-advisor-backend .
docker run -p 8000:8000 --env-file .env finance-advisor-backend
```

Test container healthcheck:
```bash
curl -f http://127.0.0.1:8000/health
```

---

## 7. Troubleshooting & Operational Runbook

* **ModuleNotFoundError: No module named 'app'**:
  * If executing directly from `backend/`, ensure `pytest.ini` contains `pythonpath = .` or run with `python -m pytest tests`.
  * If running Uvicorn from repository root, use `uvicorn backend.app.main:app`.
* **Missing Gemini Key (HTTP 503)**:
  * When `GEMINI_API_KEY` is omitted, `/api/v1/advisor/ask` responds with a controlled HTTP 503: *"Gemini API key is not configured"*.
  * Market data and document status endpoints are unaffected.
* **Upstream Market API Rate Limits (HTTP 502 / status: rate_limited)**:
  * The backend traps HTTP 429 from `api.gold-api.com` and provides graceful structured error responses.
* **Chroma Vector Store Path Resolution**:
  * Paths are anchored to `BACKEND_DIR` in `app/core/config.py`. Even when invoked from the repository root, the database path automatically resolves to `backend/chroma_langchain_db/`, eliminating duplicate empty collections.
