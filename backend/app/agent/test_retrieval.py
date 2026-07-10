"""CLI test script for retrieval pipeline.

Run: python -m app.agent.test_retrieval "my shop's tax certificate expired"
"""

import asyncio
import sys

from app.agent.retrieval import retrieve_candidates
from app.db.session import async_session


async def test_retrieval(query: str):
    """Test the retrieval pipeline with a query and print ranked candidates."""
    print(f"\nQuery: \"{query}\"\n")
    print("-" * 80)

    async with async_session() as session:
        candidates = await retrieve_candidates(query, session)

        if not candidates:
            print("No candidates found. Make sure embeddings are generated.")
            return

        for i, c in enumerate(candidates):
            print(f"\n#{i + 1} (similarity: {c.similarity_score:.4f})")
            print(f"  Service:     {c.service_name}")
            print(f"  Department:  {c.department_name}")
            print(f"  Institution: {c.institution_name}")
            print(f"  Description: {c.description[:100]}...")
            if c.office_address:
                print(f"  Office:      {c.office_address}")

    print("\n" + "-" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.agent.test_retrieval \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    asyncio.run(test_retrieval(query))
