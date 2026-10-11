# ENVIRONMENT VARIABLES SPECIFICATION — FINANCE ADVISOR

This document defines all environment variables required or supported by the Finance Advisor backend, the components that consume them, and safe configuration procedures.

> [!IMPORTANT]
> **Zero Credential Exposure Rule**: Never commit actual API keys, secrets, or credential tokens to Git. Use `.env.example` as a template and maintain local values strictly in `.env` (which is excluded by `.gitignore`).

---

## 1. Environment Variable Inventory

| Variable Name | Component | Status | Default / Fallback | Purpose & Description |
|---|---|---|---|---|
| `GEMINI_API_KEY` | Gemini LLM (`init_chat_model` / `google-genai`) | **Required** | None | Primary authentication key for Google Gemini Developer API. Replaces the non-standard Colab Secret `sec1`. |
| `GOOGLE_API_KEY` | Gemini LLM / Google SDK | **Optional Fallback** | None | Standard fallback environment variable recognized by official Google SDKs. Used if `GEMINI_API_KEY` is unset. |
| `CHROMA_PERSIST_DIRECTORY` | Chroma Vector Store (`Chroma`) | Optional | `./chroma_langchain_db` | Filesystem directory path for persisting the embedded vector index. |
| `PDF_STORAGE_DIR` | PDF Ingestion Pipeline | Optional | `./data/pdfs` | Directory where downloaded government and tax PDFs are cached. Replaces hardcoded `/content/pdfs`. |
| `GOLD_API_BASE_URL` | Market Data Tool (`get_market_price`) | Optional | `https://api.gold-api.com/price` | Base URL for fetching gold and silver spot prices in INR. |
| `SERVER_HOST` | Gradio / Backend Server | Optional | `127.0.0.1` | Network interface to bind for local serving. |
| `SERVER_PORT` | Gradio / Backend Server | Optional | `7860` | TCP port number for local web server. |

---

## 2. Legacy / Notebook-Specific Credentials Found in Audit

| Identifier | Source | Finding & Recommendation |
|---|---|---|
| `sec1` | `google.colab.userdata.get('sec1')` in Cell 12 | **Non-standard Colab secret**. `google.colab` does not exist outside Google Colab and crashes with `ModuleNotFoundError`. Must be replaced with standard `GEMINI_API_KEY`. |
| `HF_TOKEN` | Hugging Face warning in Cell 6 output | **Optional**. Hugging Face reported an unauthenticated request warning when downloading `sentence-transformers/all-mpnet-base-v2`. Setting `HF_TOKEN` is optional but avoids rate limits on HF Hub. |

---

## 3. Safe Setup Instructions

### On Windows (PowerShell)
```powershell
# Copy template to local .env
Copy-Item .env.example .env

# Edit .env with your favorite editor and paste your Gemini API key:
notepad .env

# Alternatively set in current terminal session:
$env:GEMINI_API_KEY = "your_actual_gemini_api_key"
```

### On Linux / macOS (Bash / Zsh)
```bash
# Copy template to local .env
cp .env.example .env

# Export variable directly:
export GEMINI_API_KEY="your_actual_gemini_api_key"
```

---

## 4. Security Verification Checklist

- [x] `.env` is listed in `.gitignore`.
- [x] `.env.example` contains only placeholder values (`your-gemini-api-key-here`).
- [x] Zero API keys are hardcoded in test scripts or repository files.
- [x] Test suite checks for credential presence without printing or logging key strings.
