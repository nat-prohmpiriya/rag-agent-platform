"""Project schemas for API request/response."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: uuid.UUID
    name: str
    description: str | None
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for paginated project list response."""

    items: list[ProjectResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ProjectDetailResponse(BaseModel):
    """Schema for project detail with counts."""

    id: uuid.UUID
    name: str
    description: str | None
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    document_count: int
    conversation_count: int

    model_config = ConfigDict(from_attributes=True)


class AssignDocumentsRequest(BaseModel):
    """Schema for assigning documents to a project."""

    document_ids: list[uuid.UUID] = Field(..., min_length=1)


class RemoveDocumentsRequest(BaseModel):
    """Schema for removing documents from a project."""

    document_ids: list[uuid.UUID] = Field(..., min_length=1)


class ProjectDocumentResponse(BaseModel):
    """Schema for project-document relationship response."""

    id: uuid.UUID
    project_id: uuid.UUID
    document_id: uuid.UUID
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)
