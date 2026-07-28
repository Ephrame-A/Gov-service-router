"""Generate embeddings for all services that don't have one yet.

Run: python -m app.agent.generate_embeddings
"""

import asyncio

from sqlalchemy import select

from app.agent.embeddings import get_embedding
from app.db.models import Service
from app.db.session import async_session


async def generate_embeddings():
    """Generate and store embeddings for all services missing them."""
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.embedding.is_(None))
        )
        services = result.scalars().all()

        if not services:
            print("All services already have embeddings.")
            return

        print(f"Generating embeddings for {len(services)} services...")

        for i, service in enumerate(services):
            # Build embedding text from name, description, and example phrasings
            text_parts = [
                f"Service: {service.name}",
                f"Description: {service.description}",
            ]
            if service.example_phrasings:
                text_parts.append(
                    "Example requests: " + " | ".join(service.example_phrasings)
                )

            embedding_text = "\n".join(text_parts)
            embedding = await get_embedding(embedding_text)
            service.embedding = embedding

            print(f"  [{i + 1}/{len(services)}] {service.name}")

        await session.commit()
        print("Done! All embeddings generated.")


if __name__ == "__main__":
    asyncio.run(generate_embeddings())
