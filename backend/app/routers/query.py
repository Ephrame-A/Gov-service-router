"""Query endpoint — POST /api/query."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_service(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """Accept a citizen's problem description and return the best matching government service."""
    # Placeholder — will be implemented in Milestone 2
    from app.agent.pipeline import run_pipeline

    result = await run_pipeline(request.text, request.conversation_id, db)
    return result
