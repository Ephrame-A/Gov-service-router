"""Main agent pipeline — orchestrates intent extraction, retrieval, and re-ranking."""

import uuid
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.intent import extract_intent
from app.agent.rerank import rerank_candidates
from app.agent.retrieval import retrieve_candidates
from app.config import get_settings
from app.db.models import CitizenQuery
from app.schemas import (
    Candidate,
    Intent,
    OfficeInfo,
    QueryResponse,
    QueryStatus,
    ServiceRecommendation,
)

settings = get_settings()
logger = logging.getLogger(__name__)


def _candidate_to_recommendation(
    candidate: Candidate, confidence: float, explanation: str
) -> ServiceRecommendation:
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


async def _load_conversation_context(
    conversation_id: str | None, db: AsyncSession
) -> str:
    """Load prior messages in a conversation to build context for follow-ups."""
    if not conversation_id:
        return ""

    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        return ""

    result = await db.execute(
        select(CitizenQuery)
        .where(CitizenQuery.conversation_id == conv_uuid)
        .order_by(CitizenQuery.created_at.asc())
        .limit(5)
    )
    prior = result.scalars().all()
    if not prior:
        return ""

    parts = [f"Previous message: {q.raw_text}" for q in prior]
    return "\n".join(parts) + "\n\n"


def _build_query_text(raw_text: str, context: str) -> str:
    if context:
        return f"{context}Current message: {raw_text}"
    return raw_text


async def _process_single_intent(
    text: str, intent: Intent, db: AsyncSession
) -> tuple[QueryStatus, ServiceRecommendation | None, list[ServiceRecommendation], str | None, list[ServiceRecommendation]]:
    """Process one intent and return status, recommendation, alternatives, question, top_candidates."""
    query_text = intent.query_text or text
    candidates = await retrieve_candidates(query_text, db)
    rerank_result = await rerank_candidates(query_text, candidates)

    best_candidate = next(
        (c for c in candidates if c.service_id == rerank_result.best_match_id), None
    )
    alternatives = [
        _candidate_to_recommendation(c, c.similarity_score, "Alternative match")
        for c in candidates
        if c.service_id != rerank_result.best_match_id
    ][:2]

    if rerank_result.is_ambiguous and rerank_result.confidence < settings.CONFIDENCE_THRESHOLD:
        logger.info(
            "Ambiguous service match for query=%r confidence=%.3f reasoning=%s",
            text,
            rerank_result.confidence,
            rerank_result.reasoning,
        )
        question = "I found more than one possible service. Could you clarify which one you need?"
        return QueryStatus.needs_clarification, None, [], question, []

    if best_candidate and rerank_result.confidence >= settings.CONFIDENCE_THRESHOLD:
        rec = _candidate_to_recommendation(
            best_candidate, rerank_result.confidence, rerank_result.reasoning
        )
        return QueryStatus.matched, rec, alternatives, None, []

    top_candidates = [
        _candidate_to_recommendation(c, c.similarity_score, "Low confidence match")
        for c in candidates[:3]
    ]
    return QueryStatus.no_match, None, [], None, top_candidates


async def run_pipeline(
    text: str, conversation_id: str | None, db: AsyncSession
) -> QueryResponse:
    """Run the full agent pipeline: intent → retrieval → rerank → response."""
    context = await _load_conversation_context(conversation_id, db)
    full_text = _build_query_text(text, context)

    intent_result = await extract_intent(full_text)
    conv_id = uuid.UUID(conversation_id) if conversation_id else uuid.uuid4()

    # Multi-intent: process each intent independently
    if intent_result.is_multi_intent and len(intent_result.intents) > 1:
        recommendations: list[ServiceRecommendation] = []
        for intent in intent_result.intents:
            status, rec, _, _, _ = await _process_single_intent(full_text, intent, db)
            if status == QueryStatus.matched and rec:
                recommendations.append(rec)

        query_record = CitizenQuery(
            raw_text=text,
            extracted_intent={
                "is_multi_intent": True,
                "intents": [i.model_dump() for i in intent_result.intents],
            },
            matched_service_id=None,
            confidence_score=recommendations[0].confidence if recommendations else 0.0,
            clarification_asked=False,
            conversation_id=conv_id,
        )
        db.add(query_record)
        await db.commit()
        await db.refresh(query_record)

        if recommendations:
            return QueryResponse(
                status=QueryStatus.matched,
                recommendation=recommendations[0],
                recommendations=recommendations,
                conversation_id=str(conv_id),
                query_id=str(query_record.id),
            )
        return QueryResponse(
            status=QueryStatus.no_match,
            conversation_id=str(conv_id),
            query_id=str(query_record.id),
        )

    # Single intent flow
    intent = intent_result.intents[0]
    status, recommendation, alternatives, question, top_candidates = (
        await _process_single_intent(full_text, intent, db)
    )

    matched_id = None
    confidence = 0.0
    clarification = status == QueryStatus.needs_clarification

    if recommendation:
        for c in await retrieve_candidates(intent.query_text or full_text, db):
            if c.service_name == recommendation.service_name:
                matched_id = uuid.UUID(c.service_id)
                confidence = recommendation.confidence
                break

    query_record = CitizenQuery(
        raw_text=text,
        extracted_intent=intent.model_dump(),
        matched_service_id=matched_id,
        confidence_score=confidence or None,
        clarification_asked=clarification,
        conversation_id=conv_id,
    )
    db.add(query_record)
    await db.commit()
    await db.refresh(query_record)

    query_id = str(query_record.id)

    if status == QueryStatus.needs_clarification:
        return QueryResponse(
            status=QueryStatus.needs_clarification,
            question=question,
            conversation_id=str(conv_id),
            query_id=query_id,
        )
    if status == QueryStatus.matched and recommendation:
        return QueryResponse(
            status=QueryStatus.matched,
            recommendation=recommendation,
            alternatives=alternatives,
            conversation_id=str(conv_id),
            query_id=query_id,
        )
    return QueryResponse(
        status=QueryStatus.no_match,
        top_candidates=top_candidates,
        conversation_id=str(conv_id),
        query_id=query_id,
    )
