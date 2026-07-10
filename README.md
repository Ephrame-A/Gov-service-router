# Government Service Router

An LLM-powered web application that routes citizens to the correct government office based on their problem description. Built for Addis Ababa, Ethiopia.

## Architecture

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+ with pgvector extension
- **LLM:** Gemini 2.5 Flash (intent extraction + re-ranking)
- **Embeddings:** Gemini text-embedding-004

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- A Gemini API key ([get one here](https://aistudio.google.com/apikey))

### 2. Setup

```bash
# Clone and enter the project
cd gov-service-router

# Copy environment file and add your API key
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your-key-here

# Start PostgreSQL with pgvector
docker compose up postgres -d

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed the database with sample data
python -m app.db.seed

# Generate embeddings for all services
python -m app.agent.generate_embeddings

# Start the backend
uvicorn app.main:app --reload --port 8000
```

### 3. Test the retrieval pipeline

```bash
cd backend
python -m app.agent.test_retrieval "my shop's tax certificate expired"
```

### 4. Test the API

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "I need to renew my passport"}'
```

### 5. Frontend (Milestone 3+)

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
gov-service-router/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment variables & constants
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── db/
│   │   │   ├── models.py        # SQLAlchemy ORM models
│   │   │   ├── session.py       # Async database session
│   │   │   └── seed.py          # Database seed script
│   │   ├── routers/
│   │   │   ├── query.py         # POST /api/query
│   │   │   └── feedback.py      # POST /api/feedback
│   │   └── agent/
│   │       ├── intent.py        # LLM intent extraction
│   │       ├── retrieval.py     # Embedding + pgvector search
│   │       ├── rerank.py        # LLM re-ranking
│   │       └── pipeline.py      # Orchestrates the agent pipeline
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   └── requirements.txt
├── frontend/                    # Next.js citizen & officer UI
├── docker-compose.yml
└── .env.example
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/query` | Submit a citizen query for routing |
| POST | `/api/feedback` | Submit feedback on a query result |
| GET | `/health` | Health check |

## Milestones

- [x] Milestone 0 — Infrastructure (Docker, DB, seed data)
- [x] Milestone 1 — Retrieval pipeline
- [x] Milestone 2 — Full pipeline + API
- [ ] Milestone 3 — Citizen UI
- [ ] Milestone 4 — Clarification + multi-intent
- [ ] Milestone 5 — Officer dashboard
- [ ] Milestone 6 — Deploy
