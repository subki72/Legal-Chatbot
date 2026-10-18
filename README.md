# Indonesian Legal RAG Intelligence System

[![CI Pipeline](https://github.com/subki72/Legal-Chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/subki72/Legal-Chatbot/actions)
[![Maturity Grade: Production](https://img.shields.io/badge/Maturity%20Grade-Production%20(74.8%2F100)-success.svg)](https://github.com/subki72/Legal-Chatbot)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Gateway-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Multi--Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-Advanced_RAG-orange?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-26%2F26%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)

![Code Style](https://img.shields.io/badge/Code%20Style-Senior%20Standards-black?style=for-the-badge)

An enterprise production-grade AI statutory legal assistant built for compliance verification and regulatory literacy using **Indonesian Law No. 22 of 2009 (Road Traffic and Road Transportation)**.

The system is powered by an **Advanced RAG (Retrieval-Augmented Generation)** pipeline with semantic search over a 203-page statutory corpus, per-request engine isolation for thread safety, transparent legal article citations, and flexible **Dual-Mode LLM Serving** (Local Ollama or Cloud Groq API).

---

## System Architecture

```
User Request (Port 80)
        |
   [Nginx Gateway]         -- Reverse proxy, rate limiting, security headers
        |
   [FastAPI Backend]       -- RAG inference engine, X-API-Key authentication
        |
   [ChromaDB]              -- Persistent vector store (dense embeddings)
        |
   [Ollama / Groq]         -- LLM generation (local CPU or cloud API)
```

**Key Components:**

- **Nginx Ingress Gateway**: Reverse proxy on port 80, WebSocket tunneling for Streamlit (`/_stcore/stream`), rate limiting (20 req/min), and standard security headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`).
- **FastAPI RAG Backend**: Pydantic v2 validation, SlowAPI rate limiting, X-API-Key header authentication, per-request concurrency-safe engine instances, asynchronous inference via `achat()`.
- **Dynamic LLM Factory**: Runtime provider selection between **Local Ollama** (`qwen2.5:7b`, `llama3:latest`, others) and **Cloud Groq** (`llama-3.3-70b-versatile`) via a single `.env` variable change — zero code changes required.
- **ChromaDB Vector Store**: HTTP-mode ChromaDB 0.6.3 server with persistent storage of BGE-small-en-v1.5 dense embeddings across all 203 pages.
- **Non-Root Container Security**: Both backend and frontend containers run as unprivileged `appuser` (UID 1000) to minimize container breakout risk.
- **Enterprise Structured Logging**: JSON log output compatible with Datadog, Grafana Loki, CloudWatch, and ELK Stack ingestion.
- **Incident Alerting**: Asynchronous webhook dispatch to Discord/Slack/Telegram on HTTP 500 and provider quota exhaustion (HTTP 429).
- **Senior Code Standards**: Python 3.10+ type annotations, Google-style docstrings, guard clauses, no silent failures, and no print-over-logging across all modules.

---

## Quickstart

### 1. Prerequisites

| Requirement | Notes |
|---|---|
| **Git** | For cloning the repository |
| **Docker Desktop** | Engine must be running before executing any `docker compose` commands |
| **Ollama** (Optional) | Required only when running local inference mode (`LLM_PROVIDER=ollama`) |
| **Python 3.10+** (Optional) | Required only when running tests locally outside Docker |

---

### 2. Environment Configuration

Copy the configuration template:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# Linux / macOS
cp .env.example .env
```

Edit `.env` and choose your LLM serving mode:

**Option A: Local Mode (Ollama - Recommended, no API costs)**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=300.0
APP_API_KEY=sk-legal-production-secret-98765
```

**Option B: Cloud API Mode (Groq)**
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
APP_API_KEY=sk-legal-production-secret-98765
```

> **Note**: `APP_API_KEY` is required for all requests. It is shared between the frontend and backend services for internal API authorization.

---

### 3. Launch the Stack

Build images and start all four services:

```bash
docker compose up --build -d
```

Verify that all containers are running and healthy:

```bash
docker compose ps
```

Expected output: four services in `Up` or `Up (healthy)` state.

---

### 4. Service Endpoints

| Component | URL | Description |
|---|---|---|
| **Production Gateway (Nginx)** | http://localhost | Primary production entrypoint on port 80 |
| **Web Interface (Streamlit)** | http://localhost:8501 | Direct Streamlit container access |
| **System Health Check** | http://localhost/health | AI engine status, ChromaDB connectivity, active model |
| **REST API Chat** | http://localhost/api/chat | RAG inference endpoint (requires `X-API-Key` header) |
| **API Documentation** | http://localhost:8000/docs | OpenAPI schema browser (disabled in production mode) |

---

### 5. Running the Test Suite

Execute all 26 automated unit, validation, and evaluation tests:

```bash
pytest
```

Expected output: `26 passed` in approximately 10 seconds.

---

### 6. Adding New Legal Documents

Place additional PDF regulations in `Data/raw/` and trigger re-indexing:

```bash
docker compose exec backend python backend/app/ingest.py
```

---

### 7. ChromaDB Backup

Generate a timestamped compressed snapshot with automated 7-archive retention:

```bash
python scripts/backup_chromadb.py
```

Archives are saved to `backups/chromadb_backup_YYYYMMDD_HHMMSS.tar.gz`.

---

### 8. Container Lifecycle

```bash
# Stop all containers (preserve vector database)
docker compose stop

# Restart stopped containers
docker compose start

# Single-Command Local Automation (Makefile):
make install       # Install pinned locked dependencies
make test          # Run 26 automated unit and evaluation tests
make lint          # Run Ruff static code analysis
make run           # Launch FastAPI backend service locally
make docker-build  # Build production hardened Docker container

# Stop and remove all containers and volumes
docker compose down -v
```

---

## Project Structure

```
Legal-Chatbot/
├── .github/
│   ├── dependabot.yml              # Automated weekly dependency vulnerability scanner
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI: lint, compose validation, pytest, Trivy
├── src/                            # Modular production architecture facade
│   ├── __init__.py                 # Package identifier
│   └── chatbot.py                  # Public legal assistant interface
├── backend/
│   ├── main.py                     # FastAPI entrypoint, lifespan, health check
│   ├── requirements.txt            # Backend dependencies with version bounds
│   └── app/
│       ├── config.py               # Pydantic v2 settings, provider credentials validation
│       ├── api.py                  # Chat endpoint, rate limiting, webhook alerting
│       ├── engine.py               # LlamaIndex RAG pipeline, dynamic LLM factory
│       ├── ingest.py               # PyPDF document extractor, chunking, ChromaDB indexer
│       ├── logging_config.py       # JSON structured logging formatter
│       └── utils.py                # Token estimator, citation formatter, ChromaDB heartbeat
├── frontend/
│   ├── app.py                      # Streamlit UI with telemetry badges and citation inspector
│   └── requirements.txt            # Frontend dependencies
├── nginx/
│   └── nginx.conf                  # Nginx production reverse proxy configuration
├── scripts/
│   └── backup_chromadb.py          # Automated vector database backup and retention tool
├── tests/
│   ├── conftest.py                 # pytest fixtures and environment setup
│   ├── test_api_auth.py            # X-API-Key security and rejection tests
│   ├── test_engine_provider.py     # LLM factory instantiation tests
│   ├── test_health.py              # Health check and root endpoint tests
│   ├── test_rag_evaluation.py      # Golden QA and anti-hallucination evaluation
│   ├── test_utils.py               # Token estimation and citation deduplication tests
│   ├── test_validation.py          # Pydantic input validation tests
│   └── data/
│       └── golden_legal_qa.json    # 15 ground-truth statutory QA benchmark cases
├── Data/
│   ├── raw/                        # Source PDF documents (UU Nomor 22 Tahun 2009.pdf)
│   └── chroma/                     # Persistent ChromaDB vector storage
├── docs/
│   ├── 01-project-documentation/   # Operational runbook and deployment guide
│   ├── 02-workflows/               # Implementation tracing and per-file workflow logs
│   └── 04-audits-logs/             # Production readiness audit reports
├── .env.example                    # Configuration template
├── .pre-commit-config.yaml         # Pre-commit quality & hygiene hooks
├── CHANGELOG.md                    # Keep a Changelog semantic release history
├── CONTRIBUTING.md                 # Contribution and peer review guidelines
├── docker-compose.yml              # 4-service orchestration (ChromaDB, Backend, Frontend, Gateway)
├── Dockerfile                      # Production hardened non-root containerfile
├── Dockerfile.backend              # Backend container specification
├── Dockerfile.frontend             # Streamlit container specification
├── LICENSE                         # Formal MIT open-source license
├── Makefile                        # Single-command workflow automation
├── requirements.txt                # Strictly pinned production dependencies manifest
├── requirements-lock.txt           # Deterministic locked dependencies
├── ruff.toml                       # Ruff linter and formatter configuration
└── uv.lock                         # Fast deterministic uv lockfile
```

---

## Security & Governance

- **Vulnerability Reporting**: See [SECURITY.md](SECURITY.md) for our responsible disclosure policy.
- **Contribution Guidelines**: Setup workflow and pull request standards in [CONTRIBUTING.md](CONTRIBUTING.md).
- **Changelog**: Semantic versioning and upgrade notes in [CHANGELOG.md](CHANGELOG.md).
- **License**: Explicitly licensed under the [MIT License](LICENSE).

---

## Legal Disclaimer

This system is an informational and regulatory literacy tool synthesizing official statutory text from Law No. 22 of 2009 (UU No. 22 Tahun 2009). Responses are generated from retrieved document context and do not constitute legal advice. For formal legal proceedings, consult the official State Gazette of the Republic of Indonesia and licensed legal practitioners.

