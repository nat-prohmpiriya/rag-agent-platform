"""add_message_fulltext_search

Revision ID: d5e6f7g8h9i0
Revises: 4b61be4d9675
Create Date: 2025-12-03 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5e6f7g8h9i0'
down_revision: Union[str, None] = '4b61be4d9675'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add search_vector column
    op.add_column(
        'messages',
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True)
    )

    # Create GIN index for full-text search
    op.create_index(
        'ix_messages_search_vector',
        'messages',
        ['search_vector'],
        unique=False,
        postgresql_using='gin'
    )

    # Create function to update search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION messages_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', COALESCE(NEW.content, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to auto-update search_vector on INSERT/UPDATE
    op.execute("""
        CREATE TRIGGER messages_search_vector_trigger
        BEFORE INSERT OR UPDATE OF content ON messages
        FOR EACH ROW
        EXECUTE FUNCTION messages_search_vector_update();
    """)

    # Update existing rows
    op.execute("""
        UPDATE messages
        SET search_vector = to_tsvector('english', COALESCE(content, ''))
        WHERE search_vector IS NULL;
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS messages_search_vector_trigger ON messages;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS messages_search_vector_update();")

    # Drop index
    op.drop_index('ix_messages_search_vector', table_name='messages')

    # Drop column
    op.drop_column('messages', 'search_vector')
