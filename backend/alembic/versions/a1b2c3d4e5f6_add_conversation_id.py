"""add conversation_id to citizen_queries

Revision ID: a1b2c3d4e5f6
Revises: 02fc6947aef1
Create Date: 2026-07-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "02fc6947aef1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "citizen_queries",
        sa.Column("conversation_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_citizen_queries_conversation_id",
        "citizen_queries",
        ["conversation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_citizen_queries_conversation_id", table_name="citizen_queries")
    op.drop_column("citizen_queries", "conversation_id")
