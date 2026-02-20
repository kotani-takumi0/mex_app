"""ダッシュボードAPIエンドポイント"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.application.usage_service import DashboardData, DashboardService
from app.auth.dependencies import CurrentUser, get_current_user_dependency

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_service: DashboardService | None = None


def get_service() -> DashboardService:
    global _service
    if _service is None:
        _service = DashboardService()
    return _service


class DashboardUserResponse(BaseModel):
    display_name: str
    username: str | None
    bio: str | None
    github_url: str | None


class DashboardStatsResponse(BaseModel):
    total_projects: int
    total_devlog_entries: int
    total_notebooks: int
    has_mcp_tokens: bool


class DashboardProjectResponse(BaseModel):
    id: str
    title: str
    description: str | None
    technologies: list[str]
    repository_url: str | None
    demo_url: str | None
    status: str
    is_public: bool
    devlog_count: int
    created_at: str
    updated_at: str


class DashboardResponse(BaseModel):
    user: DashboardUserResponse
    stats: DashboardStatsResponse
    recent_projects: list[DashboardProjectResponse]


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        data = service.get_dashboard(current_user.user_id)
        return _to_response(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def _to_response(data: DashboardData) -> DashboardResponse:
    return DashboardResponse(
        user=DashboardUserResponse(
            display_name=data.user.display_name,
            username=data.user.username,
            bio=data.user.bio,
            github_url=data.user.github_url,
        ),
        stats=DashboardStatsResponse(
            total_projects=data.stats.total_projects,
            total_devlog_entries=data.stats.total_devlog_entries,
            total_notebooks=data.stats.total_notebooks,
            has_mcp_tokens=data.stats.has_mcp_tokens,
        ),
        recent_projects=[
            DashboardProjectResponse(
                id=p.id,
                title=p.title,
                description=p.description,
                technologies=p.technologies,
                repository_url=p.repository_url,
                demo_url=p.demo_url,
                status=p.status,
                is_public=p.is_public,
                devlog_count=p.devlog_count,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in data.recent_projects
        ],
    )
