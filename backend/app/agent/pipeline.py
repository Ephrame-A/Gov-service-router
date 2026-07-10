"""Main agent pipeline — orchestrates intent extraction, retrieval, and re-ranking."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.intent import extract_intent
from app.agent.rerank import rerank_candidates
from app.agent.retrieval import retrieve_candidates
from app.config import get_settings
from app.db.models import CitizenQuery
from app.schemas import (
    Candidate,
    OfficeInfo,
    QueryResponse,
    QueryStatus,
    ServiceRecommendation,
)

settings = get_settings()


def _candidate_to_recommendation(candidate: Candidate, confidence: float, explanation: str) -> ServiceRecommendation:
    """Convert a retrieval Candidate to a ServiceRecommendation for the API response."""
    office = None
    if candidate.office_address:
        office = OfficeInfo(
            address=candidate.office_address,
            working_hours=candidate.working_hours,
            contact_phone=candidate.contact_phone,
            contact_email=candidate.contact_email,
        )

    return ServiceRecommendation(
        institution=candidate.institution_name,
        department=candidate.department_name,
        office=office,
        service_name=candidate.service_name,
        required_documents=candidate.required_documents,
        confidence=confidence,
        explanation=explanation,
    )


async def run_pipeline(
    text: str, conversation_id: str | None, db: AsyncSession
) -> QueryResponse:
    """Run the full agent pipeline: intent → retrieval → rerank → response.

    Logs every call to citizen_queries table.
    """
    # Step 1: Extract intent
    intent = await extract_intent(text)

    # Step 2: Retrieve candidates via embedding similarity
    candidates = await retrieve_candidates(text, db)

    # Step 3: Re-rank candidates with LLM
    rerank_result = await rerank_candidates(text, candidates)

    # Find the best matching candidate
    best_candidate = None
    for c in candidates:
        if c.service_id == rerank_result.best_match_id:
            best_candidate = c
            break

    # Build alternatives (other candidates, excluding best match)
    alternatives = [
        _candidate_to_recommendation(c, c.similarity_score, "Alternative match")
        for c in candidates
        if c.service_id != rerank_result.best_match_id
    ][:2]  # Max 2 alternatives

    # Log the query
    query_record = CitizenQuery(
        raw_text=text,
        extracted_intent={"category": intent.category, "sub_intent": intent.sub_intent, "entities": intent.entities},
        matched_service_id=uuid.UUID(rerank_result.best_match_id) if best_candidate else None,
        confidence_score=rerank_result.confidence,
        clarification_asked=rerank_result.is_ambiguous and rerank_result.confidence < settings.CONFIDENCE_THRESHOLD,
    )
    db.add(query_record)
    await db.commit()
    await db.refresh(query_record)

    query_id = str(query_record.id)

    # Decide response status based on confidence and ambiguity
    if rerank_result.is_ambiguous and rerank_result.confidence < settings.CONFIDENCE_THRESHOLD:
        # Needs clarification
        return QueryResponse(
            status=QueryStatus.needs_clarification,
            question=f"Your request could match multiple services. {rerank_result.reasoning} Could you provide more details?",
            conversation_id=conversation_id or query_id,
            query_id=query_id,
        )
    elif best_candidate and rerank_result.confidence >= settings.CONFIDENCE_THRESHOLD:
        # Confident match
        return QueryResponse(
            status=QueryStatus.matched,
            recommendation=_candidate_to_recommendation(
                best_candidate, rerank_result.confidence, rerank_result.reasoning
            ),
            alternatives=alternatives,
            query_id=query_id,
        )
    else:
        # No confident match
        top_candidates = [
            _candidate_to_recommendation(c, c.similarity_score, "Low confidence match")
            for c in candidates[:3]
        ]
        return QueryResponse(
            status=QueryStatus.no_match,
            top_candidates=top_candidates,
            query_id=query_id,
        )
