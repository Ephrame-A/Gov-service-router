"""Embedding-based candidate retrieval using pgvector."""

from google import genai

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.schemas import Candidate

settings = get_settings()


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text using Gemini."""
    client = genai.Client(api_key=settings.effective_embedding_api_key)

    result = await client.aio.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text,
    )

    return result.embeddings[0].values


async def retrieve_candidates(
    text: str, db: AsyncSession, k: int | None = None
) -> list[Candidate]:
    """Embed the query text and retrieve top-k similar services via pgvector cosine search."""
    if k is None:
        k = settings.RETRIEVAL_TOP_K

    query_embedding = await get_embedding(text)
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    sql = sql_text("""
        SELECT
            s.id,
            s.name AS service_name,
            s.description,
            s.required_documents,
            s.typical_duration,
            s.fees,
            d.name AS department_name,
            i.name AS institution_name,
            o.address AS office_address,
            o.working_hours,
            o.contact_phone,
            o.contact_email,
            1 - (s.embedding <=> :embedding::vector) AS similarity
        FROM services s
        JOIN departments d ON s.department_id = d.id
        JOIN institutions i ON d.institution_id = i.id
        LEFT JOIN offices o ON s.office_id = o.id
        WHERE s.embedding IS NOT NULL
        ORDER BY s.embedding <=> :embedding::vector
        LIMIT :k
    """)

    result = await db.execute(sql, {"embedding": embedding_str, "k": k})
    rows = result.fetchall()

    candidates = []
    for row in rows:
        candidates.append(
            Candidate(
                service_id=str(row.id),
                service_name=row.service_name,
                description=row.description,
                department_name=row.department_name,
                institution_name=row.institution_name,
                similarity_score=float(row.similarity),
                office_address=row.office_address,
                working_hours=row.working_hours,
                contact_phone=row.contact_phone,
                contact_email=row.contact_email,
                required_documents=row.required_documents or [],
                typical_duration=row.typical_duration,
                fees=row.fees,
            )
        )

    return candidates
