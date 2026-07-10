"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import query, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Tables are managed via Alembic migrations, not auto-create
    yield


app = FastAPI(
    title="Government Service Router",
    description="Routes citizens to the correct government office based on their problem description.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])


@app.get("/health")
async def health():
    return {"status": "ok"}
