"""公開ポートフォリオAPI"""

import re

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    DevLogEntry,
    Project,
    User,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


class PublicUserResponse(BaseModel):
    display_name: str
    bio: str | None
    github_url: str | None


class PublicProjectResponse(BaseModel):
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


class PublicPortfolioResponse(BaseModel):
    user: PublicUserResponse
    projects: list[PublicProjectResponse]


class PublicDevLogEntry(BaseModel):
    entry_type: str
    summary: str
    technologies: list[str]
    created_at: str


class PublicProjectDetailResponse(BaseModel):
    project: PublicProjectResponse
    devlog: list[PublicDevLogEntry]


_USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{1,28}[a-z0-9]$")


def _validate_username(username: str) -> str:
    """usernameの形式を検証"""
    if not _USERNAME_PATTERN.match(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username format",
        )
    return username


@router.get("/{username}", response_model=PublicPortfolioResponse)
async def get_public_portfolio(
    username: str = Path(..., min_length=3, max_length=30),
    db: Session = Depends(get_db),
):
    _validate_username(username)

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    projects = (
        db.query(Project)
        .filter(Project.user_id == user.id, Project.is_public.is_(True))
        .order_by(Project.updated_at.desc())
        .all()
    )

    project_responses = [
        PublicProjectResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            technologies=p.technologies or [],
            repository_url=p.repository_url,
            demo_url=p.demo_url,
            status=p.status,
            is_public=p.is_public,
            devlog_count=db.query(DevLogEntry).filter(DevLogEntry.project_id == p.id).count(),
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else "",
        )
        for p in projects
    ]

    return PublicPortfolioResponse(
        user=PublicUserResponse(
            display_name=user.display_name,
            bio=user.bio,
            github_url=user.github_url,
        ),
        projects=project_responses,
    )


@router.get("/{username}/{project_id}", response_model=PublicProjectDetailResponse)
async def get_public_project_detail(
    username: str = Path(..., min_length=3, max_length=30),
    project_id: str = Path(...),
    db: Session = Depends(get_db),
):
    _validate_username(username)

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == user.id,
            Project.is_public.is_(True),
        )
        .first()
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    devlog_entries = (
        db.query(DevLogEntry)
        .filter(DevLogEntry.project_id == project.id)
        .order_by(DevLogEntry.created_at.desc())
        .all()
    )

    return PublicProjectDetailResponse(
        project=PublicProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            technologies=project.technologies or [],
            repository_url=project.repository_url,
            demo_url=project.demo_url,
            status=project.status,
            is_public=project.is_public,
            devlog_count=db.query(DevLogEntry).filter(DevLogEntry.project_id == project.id).count(),
            created_at=project.created_at.isoformat() if project.created_at else "",
            updated_at=project.updated_at.isoformat() if project.updated_at else "",
        ),
        devlog=[
            PublicDevLogEntry(
                entry_type=e.entry_type,
                summary=e.summary,
                technologies=e.technologies or [],
                created_at=e.created_at.isoformat() if e.created_at else "",
            )
            for e in devlog_entries
        ],
    )
