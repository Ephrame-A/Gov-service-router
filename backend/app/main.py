"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import query, feedback, auth, institutions, admin
from app.auth import get_jwt_secret
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Tables are managed via Alembic migrations, not auto-create
    get_jwt_secret()
    yield


app = FastAPI(
    title="Tequami",
    description="Routes citizens to the correct government office based on their problem description.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in get_settings().CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(institutions.router, prefix="/api", tags=["institutions"])
app.include_router(admin.router, prefix="/api", tags=["admin"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    from app.config import get_settings

    s = get_settings()
    return {
        "service": "Tequami API",
        "docs": "/docs",
        "llm_enabled": s.llm_enabled,
        "gemini_model": s.gemini_model,
        "embedding_model": s.EMBEDDING_MODEL,
    }
