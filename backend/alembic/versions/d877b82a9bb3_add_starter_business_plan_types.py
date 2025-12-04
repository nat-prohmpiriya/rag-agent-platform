"""add_starter_business_plan_types

Revision ID: d877b82a9bb3
Revises: 7a4ee58279b3
Create Date: 2025-12-04 22:20:28.233788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd877b82a9bb3'
down_revision: Union[str, None] = '7a4ee58279b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum values to plantype
    op.execute("ALTER TYPE plantype ADD VALUE IF NOT EXISTS 'STARTER'")
    op.execute("ALTER TYPE plantype ADD VALUE IF NOT EXISTS 'BUSINESS'")


def downgrade() -> None:
    # Cannot easily remove enum values in PostgreSQL
    # Would need to recreate the type, which is complex
    pass
