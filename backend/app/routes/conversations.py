"""Conversation API routes for chat history management."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.base import BaseResponse, MessageResponse
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    ConversationSearchResponse,
    ConversationSearchResult,
    ConversationUpdate,
)
from app.schemas.conversation import (
    MessageResponse as ConversationMessageResponse,
)
from app.services import conversation as conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/search")
async def search_conversations(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(default=20, ge=1, le=50, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ConversationSearchResponse]:
    """
    Full-text search conversations by message content.

    Uses PostgreSQL tsvector with GIN index for high-performance search.
    Returns highlighted snippets with <mark> tags for frontend rendering.

    Features:
    - Millisecond search on millions of records (GIN Index)
    - Stemming support (running/runs/ran → all match)
    - Relevance ranking (ts_rank)
    - Auto-highlighted snippets (ts_headline)
    """
    ctx = get_context()
    ctx.user_id = current_user.id

    results, total = await conversation_service.search_conversations(
        db=db,
        user_id=current_user.id,
        query=q,
        limit=limit,
    )

    items = [
        ConversationSearchResult(
            conversation_id=r.conversation_id,
            title=r.title,
            snippet=r.snippet,
            match_count=r.match_count,
            rank=r.rank,
            created_at=r.created_at,
        )
        for r in results
    ]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ConversationSearchResponse(
            items=items,
            total=total,
            query=q,
        ),
    )


@router.get("")
async def list_conversations(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ConversationListResponse]:
    """
    List user's conversations with pagination.

    Sorted by updated_at descending (most recent first).
    """
    ctx = get_context()
    ctx.user_id = current_user.id

    conversations, total = await conversation_service.list_conversations(
        db=db,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
    )

    # Build response items with message count and preview
    items = []
    for conv in conversations:
        message_count = await conversation_service.get_conversation_message_count(
            db, conv.id
        )
        last_message_preview = await conversation_service.get_last_message_preview(
            db, conv.id
        )

        items.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count,
                last_message_preview=last_message_preview,
            )
        )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ConversationListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
        ),
    )


@router.post("")
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ConversationResponse]:
    """Create a new conversation."""
    ctx = get_context()
    ctx.user_id = current_user.id

    conversation = await conversation_service.create_conversation(
        db=db,
        user_id=current_user.id,
        title=data.title,
        project_id=data.project_id,
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0,
            last_message_preview=None,
        ),
    )


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ConversationDetailResponse]:
    """Get a conversation with all its messages."""
    ctx = get_context()
    ctx.user_id = current_user.id

    conversation = await conversation_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    messages = [
        ConversationMessageResponse(
            id=msg.id,
            role=msg.role.value,
            content=msg.content,
            created_at=msg.created_at,
            tokens_used=msg.tokens_used,
        )
        for msg in conversation.messages
    ]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ConversationDetailResponse(
            id=conversation.id,
            title=conversation.title,
            messages=messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        ),
    )


@router.patch("/{conversation_id}")
async def update_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ConversationResponse]:
    """Update a conversation (title)."""
    ctx = get_context()
    ctx.user_id = current_user.id

    conversation = await conversation_service.update_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=data.title,
    )

    message_count = await conversation_service.get_conversation_message_count(
        db, conversation.id
    )
    last_message_preview = await conversation_service.get_last_message_preview(
        db, conversation.id
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=message_count,
            last_message_preview=last_message_preview,
        ),
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """Delete a conversation and all its messages."""
    ctx = get_context()
    ctx.user_id = current_user.id

    await conversation_service.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Conversation deleted successfully"),
    )
