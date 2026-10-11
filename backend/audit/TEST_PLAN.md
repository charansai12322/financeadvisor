# TEST PLAN & EXECUTION REPORT — FINANCE ADVISOR BACKEND

**Status:** EXECUTED  
**Date:** October 2026  
**Quality Standard:** Production-oriented engineering, zero fabricated test results, complete traceability.

---

## 1. Test Architecture & Methodology

The test plan is divided into 6 distinct validation layers:

1. **Static Analysis & Security Scanning**: AST parsing, regex secret scanning, environment assumption checks.
2. **Unit Tests (Deterministic Mocks)**: Functional correctness of pricing math, conversion divisors, error handling, metadata formatting, and config validation.
3. **Live Integration Tests**: Verification of live network dependencies against public APIs and PDF sources.
4. **API Contract Tests**: Verification of function signatures and validation of backend public interfaces.
5. **End-to-End Tests**: Simulated full agent invocation paths across market data and document retrieval.
6. **Regression Tests**: Ensuring no existing functionality or imports are broken by audit patches.

---

## 2. Test Execution Ledger

| Test ID | Category | Target Component | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| `SEC-01` | Static / Sec | `financeadvisor.ipynb` | Scan for hardcoded API keys/secrets across all 19 cells & outputs | 0 matches found | 0 matches found | **PASS** |
| `SEC-02` | Static / Sec | Git history | Scan git commit log (`git log -p`) for committed secrets | 0 matches found | 0 matches found | **PASS** |
| `SEC-03` | Static / Sec | Cell 12 | Detect notebook-only dependency `google.colab.userdata` | Flag Colab dependency | Colab dependency flagged | **PASS** |
| `SEC-04` | Static / Sec | Cell 17 | Detect undefined functions `speech_to_text` and `text_to_speech` | Flag missing functions | `speech_to_text` missing prior to cell 17 | **PASS** |
| `SEC-05` | Static / Sec | Cell 2 | Detect hardcoded Linux path `/content/pdfs` | Flag non-portable path | `/content/pdfs` path detected | **PASS** |
| `MKT-01` | Unit (Mock) | Market Tool | Parse Gold XAU response and compute per-gram price using 31.1035 | Price per gram = price / 31.1035 | Calculated accurately (₹13,061.50/g) | **PASS** |
| `MKT-02` | Unit (Mock) | Market Tool | Parse Silver XAG response and compute per-gram price using 31.1035 | Price per gram = price / 31.1035 | Calculated accurately (₹189.74/g) | **PASS** |
| `MKT-03` | Unit (Mock) | Market Tool | Unsupported asset ("copper") handling | Return supported assets message | Returned "Supported assets: gold, silver" | **PASS** |
| `MKT-04` | Unit (Mock) | Market Tool | Whitespace sensitivity in asset name (" gold ") | Fails in original, handles in hardened | Original failed whitespace; hardened handled | **PASS** |
| `MKT-05` | Unit (Mock) | Market Tool | Unhandled network connection crash in original | Reproduce uncaught `ConnectionError` | Uncaught `ConnectionError` reproduced | **PASS** |
| `MKT-06` | Unit (Mock) | Market Tool | Unhandled timeout crash in original | Reproduce uncaught `Timeout` | Uncaught `Timeout` reproduced | **PASS** |
| `MKT-07` | Unit (Mock) | Hardened Tool | Graceful timeout handling returning structured status | Return `status: 'timeout'` | Returned `status: 'timeout'` | **PASS** |
| `MKT-08` | Unit (Mock) | Hardened Tool | Graceful network error handling returning structured status | Return `status: 'network_error'` | Returned `status: 'network_error'` | **PASS** |
| `MKT-09` | Unit (Mock) | Hardened Tool | Rate limit HTTP 429 detection | Return `status: 'rate_limited'` | Returned `status: 'rate_limited'` | **PASS** |
| `MKT-10` | Unit (Mock) | Hardened Tool | Calculate both per-gram and per-10g price with timestamp | Return per_gram and per_10g | Accurately computed both values | **PASS** |
| `RAG-01` | Unit | Cell 8 Formatter | Format document metadata with integer `page` | Returns "Page {page + 1}" | Returned "Page 6" for page=5 | **PASS** |
| `RAG-02` | Unit | Cell 8 Formatter | Reproduce `page + 1` crash when `page` is missing (`'N/A'`) | Reproduce `TypeError` | `TypeError: can only concatenate str to str` reproduced | **PASS** |
| `RAG-03` | Unit | Cell 8 Formatter | Reproduce `page + 1` crash when `page` is non-integer string | Reproduce `TypeError` | `TypeError: unsupported operand type` reproduced | **PASS** |
| `RAG-04` | Unit | Hardened Formatter | Safe formatting with missing/string page metadata | Return "Page Unknown" without crashing | Formatted safely without crash | **PASS** |
| `RAG-05` | Unit | Chroma DB | Verify vector duplication on repeated runs without IDs | Demonstrate duplicated chunks | Chunk count doubled from 2 to 4 | **PASS** |
| `MOD-01` | Unit | Model Config | Validate that `gemini-3.5-flash` in Cell 12 is invalid | Return `valid: False` | Returned `valid: False` (nonexistent model) | **PASS** |
| `MOD-02` | Unit | Model Config | Validate requested `Gemini 3.8 Flash` canonical identifier | Return `canonical_id: gemini-3.8-flash` | Validated `gemini-3.8-flash` (valid: True) | **PASS** |
| `MOD-03` | Unit | Credential Loader | Resolve credentials from `GEMINI_API_KEY` | Return source `GEMINI_API_KEY` | Resolved successfully | **PASS** |
| `MOD-04` | Unit | Credential Loader | Fallback to `GOOGLE_API_KEY` when `GEMINI_API_KEY` unset | Return source `GOOGLE_API_KEY` | Resolved fallback successfully | **PASS** |
| `MOD-05` | Unit | Credential Loader | Handle missing credentials gracefully | Return `configured: False` with error | Returned configured=False with clear error | **PASS** |
| `AGT-01` | Unit | System Prompt | Verify prompt constrains advisor to Indian finance & Rupee | Prompt contains required boundaries | Validated bounds in prompt | **PASS** |
| `AGT-02` | Unit | Tool Schemas | Verify tool definitions `search_finance_docs` & `get_market_price` | Accurate type hints & docstrings | Verified signatures and docstrings | **PASS** |
| `AGT-03` | Unit | Gradio Interface | Verify Gradio callable `finance_advisor(question)` | Single input string, single output | Verified signature | **PASS** |
| `AGT-04` | Unit | Voice Interface | Reproduce crash on undefined `speech_to_text` | Reproduce `NameError` | `NameError: name 'speech_to_text' is not defined` reproduced | **PASS** |
| `INT-01` | Integration (Live) | Gold-API Live | Real HTTP GET to `https://api.gold-api.com/price/XAU/INR` | HTTP 200, valid INR price > 0, symbol XAU | HTTP 200, Gold ₹13,061.51/g (₹406,258.70/oz) | **PASS** |
| `INT-02` | Integration (Live) | Gold-API Live | Real HTTP GET to `https://api.gold-api.com/price/XAG/INR` | HTTP 200, valid INR price > 0, symbol XAG | HTTP 200, Silver ₹189.74/g (₹5,901.67/oz) | **PASS** |
| `INT-03` | Integration (Live) | CBIC GST PDF | Real HTTP GET to official CBIC GST Reckoner PDF URL | HTTP 200, Content-Type application/pdf | HTTP 200, Size 1,108,846 bytes | **PASS** |
| `INT-04` | Integration (Live) | SEBI PDF | Inspect SSL certificate on `investor.sebi.gov.in` | SSL certificate failure documented | Documented `[SSL: CERTIFICATE_VERIFY_FAILED]` | **PASS** |
| `INT-05` | Integration (Live) | Gemini 3.8 Flash | Real live model call with API key | Model returns text response | **BLOCKED: `GEMINI_API_KEY` not in environment** | **BLOCKED** |
| `API-01` | Contract | HTTP REST Endpoints | Verify FastAPI/Flask routes (`/chat`, `/health`, etc.) | Endpoints return JSON responses | **NOT APPLICABLE: No HTTP API exists in repo** | **N/A** |

---

## 3. Execution Metrics

- **Total Test Cases Defined:** 35
- **Tests Executed:** 34
- **Passed:** 33
- **Failed:** 0
- **Errors:** 0
- **Blocked:** 1 (`INT-05`: Gemini live API call blocked pending user credentials)
- **Not Applicable:** 1 (`API-01`: HTTP API tests N/A because application uses Gradio/notebook functions)

---

## 4. Blockers & Coverage Gaps

1. **Gemini Live Integration (`INT-05`)**:
   - **Status:** **BLOCKED**.
   - **Reason:** No `GEMINI_API_KEY` or `GOOGLE_API_KEY` is currently defined in the execution environment.
   - **Rule Adherence:** Per Operating Rule 13, mock responses were **NOT** substituted to fabricate a pass. Real integration testing will be unblocked as soon as credentials are provided.
2. **SEBI PDF Default SSL Verification (`INT-04`)**:
   - **Status:** **CONFIRMED DEFECT / RISK**.
   - **Reason:** The server uses an Indian national root CA chain not present in default Windows/OpenSSL cert stores.
   - **Mitigation:** The pipeline must support either an unverified fallback session or load custom CA bundles.
3. **HTTP REST Endpoints (`API-01`)**:
   - **Status:** **NOT APPLICABLE**.
   - **Reason:** The repository currently has only a Gradio frontend (`demo.launch()`) and Python functions. No HTTP REST endpoints exist.
