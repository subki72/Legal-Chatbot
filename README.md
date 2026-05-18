# ⚖️ AI Legal Assistant - Indonesian Law (Enterprise Ready)

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-Advanced_RAG-orange?style=for-the-badge)

An intelligent, scalable chatbot designed to assist users in understanding Indonesian Law regulations. Employs **Advanced RAG** with **Re-ranking** to ensure high accuracy and context-aware responses based on official legal documents.

---

## 🚀 Architectural Upgrades (Production Ready)
- **Scalable Vector DB:** Migrated from local SQLite to a standalone **ChromaDB Client/Server** architecture within Docker Compose.
- **Asynchronous Execution:** Implemented `achat()` in FastAPI via LlamaIndex to unblock event loops, allowing the handling of high concurrent requests (50+ users).
- **Security Enhancements:** Integrated `slowapi` for Rate Limiting and strict `X-API-Key` headers to protect endpoints from abuse, spam, and injection attempts.
- **Centralized Config:** Adopted `pydantic-settings` to manage environments cleanly without violating the DRY principle.

---

##  Key Features

* **Advanced RAG Architecture:** Uses a retrieve-then-rerank approach.
* **High-Performance LLM:** Powered by **Llama 3** (via Groq API).
* **Transparent Citations:** Provides specific legal documents and page numbers.
* **Dockerized:** Fully containerized backend, frontend, and ChromaDB server.
* **Robust API Layer:** Centralized dependency injection, safe error handling, and robust Pydantic input validation.

---

## Tech Stack

* **Core Framework:** LlamaIndex
* **LLM Provider:** Groq
* **Vector Database:** ChromaDB Server
* **Embedding Model:** HuggingFace
* **Backend:** FastAPI, Pydantic Settings, SlowAPI
* **Frontend:** Streamlit

---

## Project Structure

```bash
Legal-Chatbot/
├── backend/
│   └── app/
│       ├── config.py    # Centralized Configuration
│       ├── api.py       # API Endpoints & Security
│       ├── engine.py    # RAG Logic
│       └── ingest.py    # Data ETL
├── frontend/            # Streamlit User Interface
├── Data/                # Raw PDFs & Chroma DB Volumes
└── docker-compose.yml   # Multi-container orchestration (App + Chroma)
```
