"""Project API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.base import BaseResponse, MessageResponse
from app.schemas.document import DocumentResponse
from app.schemas.project import (
    AssignDocumentsRequest,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
    RemoveDocumentsRequest,
)
from app.services import project as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ProjectResponse]:
    """Create a new project."""
    ctx = get_context()

    project = await project_service.create_project(
        db=db,
        user_id=current_user.id,
        data=data,
    )
    await db.commit()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ProjectResponse.model_validate(project),
    )


@router.get("")
async def list_projects(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ProjectListResponse]:
    """List user projects with pagination."""
    ctx = get_context()

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    projects, total = await project_service.get_projects(
        db=db,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
    )

    pages = project_service.calculate_pages(total, per_page)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ProjectListResponse(
            items=[ProjectResponse.model_validate(p) for p in projects],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.get("/{project_id}")
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ProjectDetailResponse]:
    """Get project detail with document and conversation counts."""
    ctx = get_context()

    project, doc_count, conv_count = await project_service.get_project_with_counts(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            user_id=project.user_id,
            created_at=project.created_at,
            updated_at=project.updated_at,
            document_count=doc_count,
            conversation_count=conv_count,
        ),
    )


@router.patch("/{project_id}")
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ProjectResponse]:
    """Update a project."""
    ctx = get_context()

    project = await project_service.update_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        data=data,
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.commit()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ProjectResponse.model_validate(project),
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[MessageResponse]:
    """Delete a project."""
    ctx = get_context()

    deleted = await project_service.delete_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.commit()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Project deleted successfully"),
    )


@router.post("/{project_id}/documents")
async def assign_documents(
    project_id: uuid.UUID,
    data: AssignDocumentsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[MessageResponse]:
    """Assign documents to a project."""
    ctx = get_context()

    try:
        count = await project_service.assign_documents(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
            document_ids=data.document_ids,
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message=f"{count} document(s) assigned to project"),
    )


@router.delete("/{project_id}/documents")
async def remove_documents(
    project_id: uuid.UUID,
    data: RemoveDocumentsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[MessageResponse]:
    """Remove documents from a project."""
    ctx = get_context()

    try:
        count = await project_service.remove_documents(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
            document_ids=data.document_ids,
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message=f"{count} document(s) removed from project"),
    )


@router.get("/{project_id}/documents")
async def list_project_documents(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[list[DocumentResponse]]:
    """List documents in a project."""
    ctx = get_context()

    try:
        documents = await project_service.get_project_documents(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=[DocumentResponse.model_validate(doc) for doc in documents],
    )
