"""Embedding service using LiteLLM API."""

import logging

import httpx

from app.config import settings
from app.core.telemetry import traced

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using LiteLLM API."""

    def __init__(self):
        """Initialize embedding service."""
        self.model_name = settings.embedding_model
        self.api_url = f"{settings.litellm_api_url}/embeddings"
        self.api_key = settings.litellm_api_key
        self._dimension = settings.embedding_dimension
        logger.info(f"Initialized LiteLLM embedding service: {self.model_name}")

    @traced()
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "input": text,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    @traced()
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "input": texts,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            # Sort by index to ensure correct order
            sorted_data = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_data]

    @traced()
    async def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Query text

        Returns:
            Embedding vector as list of floats
        """
        # For Gemini, query and document embeddings use the same method
        return await self.embed_text(query)

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """
    Get embedding service singleton.

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService()

    return _embedding_service
