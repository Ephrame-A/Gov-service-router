"""Intent extraction using Gemini LLM."""

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import Intent

settings = get_settings()


async def extract_intent(text: str) -> Intent:
    """Extract structured intent from a citizen's free-text query using Gemini.

    Returns an Intent with category, sub_intent, and extracted entities.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Analyze the following citizen's request to a government service center.
Extract the intent as structured JSON.

Citizen's request: "{text}"

Return a JSON object with exactly these fields:
- "category": the broad service category (e.g., "taxation", "immigration", "transport", "civil_registration", "land", "business", "utilities", "investment")
- "sub_intent": the specific action needed (e.g., "renewal", "new_application", "complaint", "status_check", "payment")
- "entities": a dict of extracted entities like document types, dates, locations mentioned

Return ONLY the JSON object, no other text.""",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "sub_intent": {"type": "string"},
                    "entities": {"type": "object"},
                },
                "required": ["category", "sub_intent", "entities"],
            },
        ),
    )

    import json

    data = json.loads(response.text)
    return Intent(**data)
