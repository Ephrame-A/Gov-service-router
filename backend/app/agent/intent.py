"""Intent extraction using Gemini LLM, with local fallback when no API key is set."""

import asyncio
import json
import logging

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import Intent, IntentExtractionResult

settings = get_settings()
logger = logging.getLogger(__name__)


def _fallback_intent(text: str) -> IntentExtractionResult:
    """Use the raw query when Gemini is unavailable."""
    return IntentExtractionResult(
        intents=[
            Intent(
                category="general",
                sub_intent="inquiry",
                entities={},
                query_text=text,
            )
        ],
        is_multi_intent=False,
    )


async def extract_intent(text: str) -> IntentExtractionResult:
    """Extract structured intent(s) from a citizen's free-text query.

    Falls back to a single local intent when GEMINI_API_KEY is not configured.
    """
    if not settings.llm_enabled:
        return _fallback_intent(text)

    try:
        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=12000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

        response = await asyncio.wait_for(client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=f"""Analyze the following citizen's request to a government service center.
Extract ALL distinct service needs. A single message may contain multiple unrelated requests.

Citizen's request: "{text}"

Return a JSON object with:
- "is_multi_intent": true if the request contains 2+ distinct, unrelated service needs
- "intents": array of objects, each with:
  - "category": broad service category (e.g., "taxation", "immigration", "transport", "civil_registration", "land", "business", "utilities", "investment")
  - "sub_intent": specific action (e.g., "renewal", "new_application", "complaint", "status_check", "payment")
  - "entities": dict of extracted entities like document types, dates, locations
  - "query_text": the portion of the citizen's text relevant to this specific need

If there is only one need, return is_multi_intent=false with a single intent.
Return ONLY the JSON object.""",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "is_multi_intent": {"type": "boolean"},
                        "intents": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "sub_intent": {"type": "string"},
                                    "entities": {"type": "object"},
                                    "query_text": {"type": "string"},
                                },
                                "required": ["category", "sub_intent", "entities", "query_text"],
                            },
                        },
                    },
                    "required": ["is_multi_intent", "intents"],
                },
            ),
        ), timeout=12)
    except Exception as exc:  # pragma: no cover - exercised via tests with patched client
        logger.exception("Intent extraction failed, falling back to local intent")
        return _fallback_intent(text)

    data = json.loads(response.text)
    intents = [Intent(**item) for item in data["intents"]]
    if not intents:
        intents = [Intent(category="general", sub_intent="inquiry", entities={}, query_text=text)]
    return IntentExtractionResult(
        intents=intents,
        is_multi_intent=data.get("is_multi_intent", len(intents) > 1),
    )
