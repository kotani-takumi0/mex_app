"""ダッシュボード統計サービス"""

from dataclasses import dataclass

from sqlalchemy import String, cast

from app.infrastructure.database.models import (
    DevLogEntry,
    MCPToken,
    Project,
    User,
)
from app.infrastructure.database.session import SessionLocal


@dataclass
class DashboardUser:
    display_name: str
    username: str | None
    bio: str | None
    github_url: str | None


@dataclass
class DashboardStats:
    total_projects: int
    total_devlog_entries: int
    total_notebooks: int
    has_mcp_tokens: bool


@dataclass
class DashboardProject:
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


@dataclass
class DashboardData:
    user: DashboardUser
    stats: DashboardStats
    recent_projects: list[DashboardProject]


class DashboardService:
    """ポートフォリオ概要の集計"""

    def get_dashboard(self, user_id: str) -> DashboardData:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise ValueError("User not found")

            total_projects = db.query(Project).filter(Project.user_id == user_id).count()
            total_devlog_entries = (
                db.query(DevLogEntry).filter(DevLogEntry.user_id == user_id).count()
            )

            # 有効な（未失効の）MCPトークンが存在するか確認
            has_mcp_tokens = (
                db.query(MCPToken)
                .filter(
                    MCPToken.user_id == user_id,
                    MCPToken.revoked_at.is_(None),
                )
                .first()
                is not None
            )

            # notebook_id を持つ DevLogEntry をカウント
            total_notebooks = (
                db.query(DevLogEntry)
                .filter(
                    DevLogEntry.user_id == user_id,
                    cast(DevLogEntry.metadata_["notebook_id"], String) != "null",
                    DevLogEntry.metadata_["notebook_id"].isnot(None),
                )
                .count()
            )

            recent_projects = (
                db.query(Project)
                .filter(Project.user_id == user_id)
                .order_by(Project.updated_at.desc())
                .limit(5)
                .all()
            )

            recent_project_summaries = [
                DashboardProject(
                    id=p.id,
                    title=p.title,
                    description=p.description,
                    technologies=p.technologies or [],
                    repository_url=p.repository_url,
                    demo_url=p.demo_url,
                    status=p.status,
                    is_public=p.is_public,
                    devlog_count=db.query(DevLogEntry)
                    .filter(DevLogEntry.project_id == p.id)
                    .count(),
                    created_at=p.created_at.isoformat() if p.created_at else "",
                    updated_at=p.updated_at.isoformat() if p.updated_at else "",
                )
                for p in recent_projects
            ]

            return DashboardData(
                user=DashboardUser(
                    display_name=user.display_name,
                    username=user.username,
                    bio=user.bio,
                    github_url=user.github_url,
                ),
                stats=DashboardStats(
                    total_projects=total_projects,
                    total_devlog_entries=total_devlog_entries,
                    total_notebooks=total_notebooks,
                    has_mcp_tokens=has_mcp_tokens,
                ),
                recent_projects=recent_project_summaries,
            )
        finally:
            db.close()
