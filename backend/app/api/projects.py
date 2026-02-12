"""プロジェクトAPI"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.application.project_service import (
    ProjectCreate,
    ProjectService,
    ProjectSummary,
    ProjectUpdate,
)
from app.auth.dependencies import CurrentUser, get_current_user_dependency

router = APIRouter(prefix="/projects", tags=["Projects"])

_service: ProjectService | None = None


def get_service() -> ProjectService:
    global _service
    if _service is None:
        _service = ProjectService()
    return _service


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., description="プロジェクト名")
    description: str | None = Field(None, description="概要")
    technologies: list[str] = Field(default_factory=list)
    repository_url: str | None = Field(None, description="GitHub URL")
    demo_url: str | None = Field(None, description="デモURL")
    status: str = Field("in_progress", description="状態")
    is_public: bool = Field(False, description="公開フラグ")


class ProjectUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    repository_url: str | None = None
    demo_url: str | None = None
    status: str | None = None
    is_public: bool | None = None


class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str | None
    technologies: list[str]
    repository_url: str | None
    demo_url: str | None
    status: str
    is_public: bool
    devlog_count: int
    quiz_score: float | None
    created_at: str
    updated_at: str


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    service = get_service()
    projects = service.list_projects(current_user.user_id)
    return ProjectListResponse(projects=[_to_response(p) for p in projects])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    service = get_service()
    project = service.create_project(
        current_user.user_id,
        ProjectCreate(
            title=request.title,
            description=request.description,
            technologies=request.technologies,
            repository_url=request.repository_url,
            demo_url=request.demo_url,
            status=request.status,
            is_public=request.is_public,
        ),
    )
    return _to_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        project = service.get_project(current_user.user_id, project_id)
        return _to_response(project)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        project = service.update_project(
            current_user.user_id,
            project_id,
            ProjectUpdate(
                title=request.title,
                description=request.description,
                technologies=request.technologies,
                repository_url=request.repository_url,
                demo_url=request.demo_url,
                status=request.status,
                is_public=request.is_public,
            ),
        )
        return _to_response(project)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        service.delete_project(current_user.user_id, project_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


def _to_response(project: ProjectSummary) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        technologies=project.technologies,
        repository_url=project.repository_url,
        demo_url=project.demo_url,
        status=project.status,
        is_public=project.is_public,
        devlog_count=project.devlog_count,
        quiz_score=project.quiz_score,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
