"""LLM-based re-ranking of retrieval candidates."""

import json

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import Candidate, RerankResult

settings = get_settings()


async def rerank_candidates(text: str, candidates: list[Candidate]) -> RerankResult:
    """Use Gemini to re-rank candidates and assess confidence.

    Receives the citizen's text plus top-k candidates from retrieval,
    returns the best match with a confidence score and reasoning.
    """
    if not candidates:
        return RerankResult(
            best_match_id="",
            confidence=0.0,
            reasoning="No candidates found.",
            is_ambiguous=False,
        )

    candidates_text = "\n".join(
        f"- ID: {c.service_id} | Service: {c.service_name} | Department: {c.department_name} "
        f"| Institution: {c.institution_name} | Description: {c.description} "
        f"| Similarity: {c.similarity_score:.3f}"
        for c in candidates
    )

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
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

    data = json.loads(response.text)
    return RerankResult(**data)
