# Government Service Router 

An LLM-powered web application that routes Ethiopian citizens to the correct government office based on their natural-language problem description. Built for Addis Ababa, Ethiopia.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![pgvector](https://img.shields.io/badge/pgvector-PostgreSQL-blue?logo=postgresql)](https://github.com/pgvector/pgvector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

Citizens describe their problem in plain language (Amharic or English). The system:
1. **Extracts intent** via Gemini LLM
2. **Retrieves** semantically similar services using pgvector embeddings
3. **Re-ranks** results with LLM scoring
4. **Asks clarifying questions** when the intent is ambiguous
5. **Routes** to the correct institution with address, contact, and required documents

Officers can manage their institution's services through a dashboard; admins approve new institution registrations.

---

## Architecture

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 (App Router) + TypeScript + Tailwind CSS + NextAuth |
| **Backend** | FastAPI (Python 3.11+) + Uvicorn |
| **Database** | PostgreSQL 15+ with **pgvector** extension |
| **LLM** | Google Gemini (`gemini-2.0-flash` by default; configurable) |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally, no API key needed |
| **Auth** | JWT (backend) + NextAuth (frontend) |
| **Deployment** | Render (backend) + Vercel (frontend) |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- A free Gemini API key → [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1. Environment Setup

```bash
git clone [<repo-url>](https://github.com/Ephrame-A/Gov-service-router)
cd gov-service-router

cp .env.example .env
# Edit .env — set GEMINI_API_KEY and NEXTAUTH_SECRET (any random 32-char string)
```

### 2. Start PostgreSQL

```bash
docker compose up postgres -d
```

### 3. Backend Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Apply DB migrations
alembic upgrade head

# Seed default institutions, services, and users
python -m app.db.seed

# Generate vector embeddings for all services
python -m app.agent.generate_embeddings

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Citizen portal: **http://localhost:3000**

### If a search cannot be completed

The frontend needs the API at `http://localhost:8000` and a populated PostgreSQL database; the example requests in the UI are prompts, not mock search results. Check `http://localhost:8000/health` first. If it is unavailable, start PostgreSQL and run the backend from `backend/` with that directory's `.venv`:

```bash
docker compose up postgres -d
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

If this is a new database, run the migrations, seed script, and embedding generator from `backend/` as described above. **Do not rerun the seed script on a populated database:** it clears the existing catalog and users before inserting sample records.

---

## Default Accounts (seeded)

| Role | Email | Password |
|---|---|---|
| Admin | `admin@govrouter.et` | `admin123` |
| Officer | `officer@govrouter.et` | `officer123` |

| Dashboard | URL |
|---|---|
| Citizen portal | http://localhost:3000 |
| Officer dashboard | http://localhost:3000/officer |
| Admin approval queue | http://localhost:3000/admin |

---

## API Reference

### Public Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/query` | Submit a citizen query for routing |
| `POST` | `/api/feedback` | Submit feedback (helpful / not helpful) on a result |
| `POST` | `/api/auth/login` | Officer / admin login → returns JWT |
| `POST` | `/api/auth/register` | Register a new officer (pending admin approval) |
| `GET` | `/health` | Health check |
| `GET` | `/` | Service info + LLM status |

### Authenticated Endpoints (JWT required)

| Method | Path | Role | Description |
|---|---|---|---|
| `GET` | `/api/institutions` | Officer+ | List all approved institutions |
| `GET` | `/api/institutions/{id}` | Officer+ | Get institution detail |
| `POST` | `/api/institutions` | Officer | Create institution (queued for admin approval) |
| `PUT` | `/api/institutions/{id}` | Officer | Update own institution |
| `POST` | `/api/services` | Officer | Add a service to own institution |
| `PUT` | `/api/services/{id}` | Officer | Update a service |
| `DELETE` | `/api/services/{id}` | Officer | Delete a service |
| `POST` | `/api/services/{id}/refresh-embedding` | Officer | Regenerate service embedding |
| `GET` | `/api/admin/pending-institutions` | Admin | List pending approvals |
| `POST` | `/api/admin/approve/{id}` | Admin | Approve institution |
| `POST` | `/api/admin/reject/{id}` | Admin | Reject institution |

### Example: Submit a Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "I need to renew my passport"}'
```

---

## Testing

```bash
cd backend
source .venv/bin/activate

# Run the full test suite
pytest -v

# Run a specific test file
pytest tests/test_api.py -v

# Test the retrieval pipeline manually
python -m app.agent.test_retrieval "my shop's tax certificate expired"
```

The test suite covers:
- API endpoint integration tests (`test_api.py`)
- Embedding generation & similarity (`test_embeddings.py`)
- Intent extraction (`test_intent.py`)
- Re-ranking logic (`test_rerank.py`)
- 25 hand-written fixture queries with expected outcomes (`test_fixture_queries.py`)

---

## Project Structure

```
gov-service-router/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── intent.py            # Gemini-powered intent extraction
│   │   │   ├── retrieval.py         # pgvector semantic search
│   │   │   ├── rerank.py            # LLM-based re-ranking
│   │   │   ├── pipeline.py          # End-to-end orchestration
│   │   │   ├── embeddings.py        # Embedding helper
│   │   │   └── generate_embeddings.py  # Offline embedding script
│   │   ├── routers/
│   │   │   ├── query.py             # POST /api/query
│   │   │   ├── feedback.py          # POST /api/feedback
│   │   │   ├── auth.py              # Login / register
│   │   │   ├── institutions.py      # CRUD for institutions & services
│   │   │   └── admin.py             # Approval queue
│   │   ├── db/
│   │   │   ├── models.py            # SQLAlchemy ORM models
│   │   │   ├── session.py           # Async DB session + dependency
│   │   │   └── seed.py              # Default data seeder
│   │   ├── auth.py                  # JWT helpers
│   │   ├── config.py                # Pydantic settings (env vars)
│   │   ├── schemas.py               # Pydantic request/response models
│   │   └── main.py                  # FastAPI app entry point
│   ├── alembic/                     # DB migration scripts
│   ├── tests/                       # pytest suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Citizen query UI
│   │   ├── officer/                 # Officer dashboard
│   │   ├── admin/                   # Admin approval queue
│   │   └── api/                     # NextAuth API routes
│   ├── components/                  # Shared UI components
│   ├── lib/
│   │   ├── api.ts                   # Typed API client
│   │   └── auth.ts                  # NextAuth config
│   ├── types/                       # TypeScript type definitions
│   ├── middleware.ts                 # Route protection
│   └── package.json
├── docker-compose.yml
├── render.yaml                      # Render deployment config
└── .env.example                     # Environment variable template
```





