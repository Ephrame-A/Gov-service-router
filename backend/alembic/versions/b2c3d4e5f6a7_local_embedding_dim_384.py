"""switch embedding column to 384-dim local model vectors

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old 768-dim Gemini embeddings and recreate as 384-dim local model vectors.
    op.drop_column("services", "embedding")
    op.add_column(
        "services",
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("services", "embedding")
    op.add_column(
        "services",
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
    )
