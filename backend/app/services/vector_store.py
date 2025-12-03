"""Vector store service for document chunk operations with pgvector."""

import logging
import uuid
from abc import ABC, abstractmethod

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.telemetry import traced
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.project_document import ProjectDocument
from app.schemas.vector import ChunkCreate, ChunkResult

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract base class for vector store operations."""

    @abstractmethod
    async def add_chunks(self, db: AsyncSession, chunks: list[ChunkCreate]) -> None:
        """
        Add document chunks with embeddings to the vector store.

        Args:
            db: Database session
            chunks: List of chunks to add
        """
        pass

    @abstractmethod
    async def search(
        self,
        db: AsyncSession,
        query_embedding: list[float],
        top_k: int,
        user_id: uuid.UUID,
        document_ids: list[uuid.UUID] | None = None,
        project_id: uuid.UUID | None = None,
    ) -> list[ChunkResult]:
        """
        Search for similar chunks using vector similarity.

        Args:
            db: Database session
            query_embedding: Query embedding vector
            top_k: Number of results to return
            user_id: User ID to filter documents by ownership
            document_ids: Optional list of document IDs to scope the search
            project_id: Optional project ID to filter documents in project

        Returns:
            List of chunk results sorted by similarity
        """
        pass

    @abstractmethod
    async def delete_by_document(self, db: AsyncSession, document_id: uuid.UUID) -> None:
        """
        Delete all chunks for a document.

        Args:
            db: Database session
            document_id: Document ID to delete chunks for
        """
        pass


class PgVectorStore(VectorStore):
    """PostgreSQL pgvector implementation of vector store."""

    @traced()
    async def add_chunks(self, db: AsyncSession, chunks: list[ChunkCreate]) -> None:
        """Add document chunks with embeddings to pgvector."""
        if not chunks:
            return

        for chunk_data in chunks:
            chunk = DocumentChunk(
                document_id=chunk_data.document_id,
                content=chunk_data.content,
                embedding=chunk_data.embedding,
                chunk_index=chunk_data.chunk_index,
                metadata_=chunk_data.metadata,
            )
            db.add(chunk)

        await db.flush()
        logger.info(f"Added {len(chunks)} chunks for document {chunks[0].document_id}")

    @traced()
    async def search(
        self,
        db: AsyncSession,
        query_embedding: list[float],
        top_k: int,
        user_id: uuid.UUID,
        document_ids: list[uuid.UUID] | None = None,
        project_id: uuid.UUID | None = None,
    ) -> list[ChunkResult]:
        """Search for similar chunks using cosine distance.

        Args:
            db: Database session
            query_embedding: Query embedding vector
            top_k: Number of results to return
            user_id: User ID to filter documents by ownership
            document_ids: Optional list of document IDs to scope the search.
                         If None, search all user's documents.
            project_id: Optional project ID to filter documents in project.
                       If provided, only searches documents assigned to that project.
        """
        # Use pgvector's cosine distance operator (<=>)
        # Lower distance = higher similarity
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)

        stmt = (
            select(
                DocumentChunk.id,
                DocumentChunk.document_id,
                DocumentChunk.content,
                DocumentChunk.chunk_index,
                DocumentChunk.metadata_.label("metadata"),
                distance.label("score"),
            )
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
            .where(DocumentChunk.embedding.isnot(None))
        )

        # Filter by project (join with ProjectDocument)
        if project_id:
            stmt = stmt.join(
                ProjectDocument,
                ProjectDocument.document_id == Document.id,
            ).where(ProjectDocument.project_id == project_id)

        # Optional: Filter by specific documents
        if document_ids:
            stmt = stmt.where(Document.id.in_(document_ids))

        stmt = stmt.order_by(distance).limit(top_k)

        result = await db.execute(stmt)
        rows = result.all()

        return [
            ChunkResult(
                id=row.id,
                document_id=row.document_id,
                content=row.content,
                chunk_index=row.chunk_index,
                score=row.score,
                metadata=row.metadata,
            )
            for row in rows
        ]

    @traced()
    async def delete_by_document(self, db: AsyncSession, document_id: uuid.UUID) -> None:
        """Delete all chunks for a document."""
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        result = await db.execute(stmt)
        await db.flush()
        logger.info(f"Deleted {result.rowcount} chunks for document {document_id}")


# Singleton instance
_vector_store: PgVectorStore | None = None


def get_vector_store() -> PgVectorStore:
    """
    Get vector store singleton.

    Returns:
        PgVectorStore instance
    """
    global _vector_store

    if _vector_store is None:
        _vector_store = PgVectorStore()

    return _vector_store
