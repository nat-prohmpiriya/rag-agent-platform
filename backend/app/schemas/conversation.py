"""Conversation and message schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Request schemas
class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    title: str | None = Field(default=None, max_length=255)
    project_id: uuid.UUID | None = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = Field(default=None, max_length=255)


# Response schemas
class MessageResponse(BaseModel):
    """Schema for message response."""

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    tokens_used: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Schema for conversation response in list."""

    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list."""

    items: list[ConversationResponse]
    total: int
    page: int
    per_page: int


class ConversationDetailResponse(BaseModel):
    """Schema for conversation with messages."""

    id: uuid.UUID
    title: str | None
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Search schemas
class ConversationSearchResult(BaseModel):
    """Schema for a single search result."""

    conversation_id: uuid.UUID
    title: str | None
    snippet: str  # Highlighted snippet with <mark> tags
    match_count: int
    rank: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationSearchResponse(BaseModel):
    """Schema for search results."""

    items: list[ConversationSearchResult]
    total: int
    query: str
