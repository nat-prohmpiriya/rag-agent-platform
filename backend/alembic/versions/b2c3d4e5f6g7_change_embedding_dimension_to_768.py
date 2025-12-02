"""change_embedding_dimension_to_768

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-02 23:25:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old HNSW index
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")

    # Change column type from vector(1024) to vector(768)
    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE vector(768)
    """)

    # Clear existing embeddings (they were created with different model)
    op.execute("UPDATE document_chunks SET embedding = NULL")

    # Recreate HNSW index with new dimension
    op.execute("""
        CREATE INDEX ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    # Drop HNSW index
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")

    # Change back to vector(1024)
    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding TYPE vector(1024)
    """)

    # Recreate HNSW index
    op.execute("""
        CREATE INDEX ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
