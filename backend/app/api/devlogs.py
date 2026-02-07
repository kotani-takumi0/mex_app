"""開発ログAPI"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.application.devlog_service import DevLogService, DevLogCreate, DevLogUpdate, DevLogSummary

router = APIRouter(prefix="/devlogs", tags=["DevLogs"])

_service: DevLogService | None = None


def get_service() -> DevLogService:
    global _service
    if _service is None:
        _service = DevLogService()
    return _service


class DevLogCreateRequest(BaseModel):
    source: str | None = Field(None, description="mcp | manual")
    entry_type: str = Field(..., description="作業種別")
    summary: str = Field(..., description="要約")
    detail: str | None = Field(None, description="詳細")
    technologies: list[str] = Field(default_factory=list)
    ai_tool: str | None = None
    metadata: dict | None = None


class DevLogUpdateRequest(BaseModel):
    source: str | None = None
    entry_type: str | None = None
    summary: str | None = None
    detail: str | None = None
    technologies: list[str] | None = None
    ai_tool: str | None = None
    metadata: dict | None = None


class DevLogEntryResponse(BaseModel):
    id: str
    project_id: str
    source: str
    entry_type: str
    summary: str
    detail: str | None
    technologies: list[str]
    ai_tool: str | None
    created_at: str
    metadata: dict


class DevLogListEntry(BaseModel):
    id: str
    project_id: str
    source: str
    entry_type: str
    summary: str
    detail: str | None
    technologies: list[str]
    ai_tool: str | None
    created_at: str
    metadata: dict


class DevLogListResponse(BaseModel):
    entries: list[DevLogListEntry]
    total: int


@router.get("/{project_id}", response_model=DevLogListResponse)
async def list_devlogs(
    project_id: str,
    limit: int | None = None,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        entries, total = service.list_entries(current_user.user_id, project_id, limit=limit)
        return DevLogListResponse(
            entries=[
                DevLogListEntry(
                    id=e.id,
                    project_id=e.project_id,
                    source=e.source,
                    entry_type=e.entry_type,
                    summary=e.summary,
                    detail=e.detail,
                    technologies=e.technologies,
                    ai_tool=e.ai_tool,
                    created_at=e.created_at,
                    metadata=e.metadata,
                )
                for e in entries
            ],
            total=total,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{project_id}/entries", response_model=DevLogEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_devlog(
    project_id: str,
    request: DevLogCreateRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        entry = service.create_entry(
            current_user.user_id,
            project_id,
            DevLogCreate(
                source=request.source or "manual",
                entry_type=request.entry_type,
                summary=request.summary,
                detail=request.detail,
                technologies=request.technologies,
                ai_tool=request.ai_tool,
                metadata=request.metadata,
            ),
        )
        return _to_entry_response(entry)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/entries/{entry_id}", response_model=DevLogEntryResponse)
async def update_devlog(
    entry_id: str,
    request: DevLogUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        entry = service.update_entry(
            current_user.user_id,
            entry_id,
            DevLogUpdate(
                source=request.source,
                entry_type=request.entry_type,
                summary=request.summary,
                detail=request.detail,
                technologies=request.technologies,
                ai_tool=request.ai_tool,
                metadata=request.metadata,
            ),
        )
        return _to_entry_response(entry)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/entries/{entry_id}")
async def delete_devlog(
    entry_id: str,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        service.delete_entry(current_user.user_id, entry_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


def _to_entry_response(entry: DevLogSummary) -> DevLogEntryResponse:
    return DevLogEntryResponse(
        id=entry.id,
        project_id=entry.project_id,
        source=entry.source,
        entry_type=entry.entry_type,
        summary=entry.summary,
        detail=entry.detail,
        technologies=entry.technologies,
        ai_tool=entry.ai_tool,
        created_at=entry.created_at,
        metadata=entry.metadata,
    )
