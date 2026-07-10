"""Feedback endpoint — POST /api/feedback."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CitizenQuery
from app.db.session import get_db
from app.schemas import FeedbackRequest

router = APIRouter()


@router.post("/feedback", status_code=204)
async def submit_feedback(request: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    """Record citizen feedback (correct/incorrect) on a query result."""
    import uuid

    try:
        query_uuid = uuid.UUID(request.query_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid query_id format")

    result = await db.execute(
        select(CitizenQuery).where(CitizenQuery.id == query_uuid)
    )
    query_record = result.scalar_one_or_none()
    if not query_record:
        raise HTTPException(status_code=404, detail="Query not found")

    query_record.feedback = request.feedback
    await db.commit()
