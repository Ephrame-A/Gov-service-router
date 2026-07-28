"""LLM-based re-ranking of retrieval candidates, with local fallback."""

import json
import logging

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import Candidate, RerankResult

settings = get_settings()
logger = logging.getLogger(__name__)


def _fallback_rerank(text: str, candidates: list[Candidate]) -> RerankResult:
    """Rank by embedding similarity when Gemini is unavailable."""
    if not candidates:
        return RerankResult(
            best_match_id="",
            confidence=0.0,
            reasoning="No matching services found in the database.",
            is_ambiguous=False,
        )

    best = candidates[0]
    confidence = max(0.0, min(1.0, best.similarity_score))

    is_ambiguous = False
    if len(candidates) >= 2:
        second = candidates[1]
        score_gap = best.similarity_score - second.similarity_score
        if score_gap < 0.05 and second.similarity_score > 0.4:
            is_ambiguous = True

    reasoning = (
        f"This service best matches your request based on semantic similarity "
        f"({confidence:.0%} match). Visit {best.institution_name} — {best.department_name}."
    )

    return RerankResult(
        best_match_id=best.service_id,
        confidence=confidence,
        reasoning=reasoning,
        is_ambiguous=is_ambiguous,
    )


async def rerank_candidates(text: str, candidates: list[Candidate]) -> RerankResult:
    """Re-rank candidates with Gemini, or fall back to similarity scores."""
    if not candidates:
        return RerankResult(
            best_match_id="",
            confidence=0.0,
            reasoning="No candidates found.",
            is_ambiguous=False,
        )

    if not settings.llm_enabled:
        return _fallback_rerank(text, candidates)

    candidates_text = "\n".join(
        f"- ID: {c.service_id} | Service: {c.service_name} | Department: {c.department_name} "
        f"| Institution: {c.institution_name} | Description: {c.description} "
        f"| Similarity: {c.similarity_score:.3f}"
        for c in candidates
    )

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=f"""You are a government service routing assistant. A citizen has described their problem,
and we've retrieved the following candidate services from our database.

CITIZEN'S REQUEST: "{text}"

CANDIDATE SERVICES:
{candidates_text}

Analyze which service best matches the citizen's request. Consider:
1. How well the service description matches the citizen's need
2. Whether the department and institution are appropriate
3. Whether the request is ambiguous and could match multiple services

Return a JSON object with:
- "best_match_id": the ID of the best matching service (use exact ID from candidates)
- "confidence": a score from 0 to 1 indicating how confident you are in the match
- "reasoning": a brief explanation of why this service is the best match, written for the citizen
- "is_ambiguous": true if the request could reasonably match 2+ services and clarification would help

Return ONLY the JSON object.""",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "best_match_id": {"type": "string"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"},
                        "is_ambiguous": {"type": "boolean"},
                    },
                    "required": ["best_match_id", "confidence", "reasoning", "is_ambiguous"],
                },
            ),
        )
    except Exception as exc:  # pragma: no cover - exercised via tests with patched client
        logger.exception("Rerank failed, falling back to local reranking")
        return _fallback_rerank(text, candidates)

    data = json.loads(response.text)
    return RerankResult(**data)
