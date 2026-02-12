"""公開ポートフォリオAPI"""

import re

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    DevLogEntry,
    Project,
    QuizAttempt,
    QuizQuestion,
    SkillScore,
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
    quiz_score: float | None
    created_at: str
    updated_at: str


class PublicSkillResponse(BaseModel):
    technology: str
    score: float
    total_questions: int
    correct_answers: int
    last_assessed_at: str | None


class PublicPortfolioResponse(BaseModel):
    user: PublicUserResponse
    projects: list[PublicProjectResponse]
    skills: list[PublicSkillResponse]


class PublicDevLogEntry(BaseModel):
    entry_type: str
    summary: str
    technologies: list[str]
    created_at: str


class QuizSummaryByTech(BaseModel):
    technology: str
    score: float
    questions: int
    correct: int


class PublicQuizSummary(BaseModel):
    total_questions: int
    correct_answers: int
    score: float
    by_technology: list[QuizSummaryByTech]


class PublicProjectDetailResponse(BaseModel):
    project: PublicProjectResponse
    devlog: list[PublicDevLogEntry]
    quiz_summary: PublicQuizSummary


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
            quiz_score=_project_quiz_score(db, p.id, user.id),
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else "",
        )
        for p in projects
    ]

    skills = (
        db.query(SkillScore)
        .filter(SkillScore.user_id == user.id)
        .order_by(SkillScore.score.desc())
        .all()
    )

    return PublicPortfolioResponse(
        user=PublicUserResponse(
            display_name=user.display_name,
            bio=user.bio,
            github_url=user.github_url,
        ),
        projects=project_responses,
        skills=[
            PublicSkillResponse(
                technology=s.technology,
                score=s.score,
                total_questions=s.total_questions,
                correct_answers=s.correct_answers,
                last_assessed_at=s.last_assessed_at.isoformat() if s.last_assessed_at else None,
            )
            for s in skills
        ],
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

    quiz_summary = _build_quiz_summary(db, project.id, user.id)

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
            quiz_score=quiz_summary.score if quiz_summary.total_questions else None,
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
        quiz_summary=quiz_summary,
    )


def _project_quiz_score(db, project_id: str, user_id: str) -> float | None:
    total = (
        db.query(QuizAttempt)
        .join(QuizQuestion, QuizAttempt.quiz_question_id == QuizQuestion.id)
        .filter(QuizQuestion.project_id == project_id, QuizAttempt.user_id == user_id)
        .count()
    )
    if total == 0:
        return None
    correct = (
        db.query(QuizAttempt)
        .join(QuizQuestion, QuizAttempt.quiz_question_id == QuizQuestion.id)
        .filter(
            QuizQuestion.project_id == project_id,
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_correct.is_(True),
        )
        .count()
    )
    return round((correct / total) * 100, 1)


def _build_quiz_summary(db, project_id: str, user_id: str) -> PublicQuizSummary:
    attempts = (
        db.query(QuizAttempt, QuizQuestion)
        .join(QuizQuestion, QuizAttempt.quiz_question_id == QuizQuestion.id)
        .filter(QuizQuestion.project_id == project_id, QuizAttempt.user_id == user_id)
        .all()
    )

    total = len(attempts)
    correct = sum(1 for attempt, _ in attempts if attempt.is_correct)
    score = round((correct / total) * 100, 1) if total else 0.0

    by_tech: dict[str, dict[str, int]] = {}
    for attempt, question in attempts:
        tech = question.technology
        if tech not in by_tech:
            by_tech[tech] = {"total": 0, "correct": 0}
        by_tech[tech]["total"] += 1
        if attempt.is_correct:
            by_tech[tech]["correct"] += 1

    by_technology = []
    for tech, counts in by_tech.items():
        tech_score = (
            round((counts["correct"] / counts["total"]) * 100, 1) if counts["total"] else 0.0
        )
        by_technology.append(
            QuizSummaryByTech(
                technology=tech,
                score=tech_score,
                questions=counts["total"],
                correct=counts["correct"],
            )
        )

    return PublicQuizSummary(
        total_questions=total,
        correct_answers=correct,
        score=score,
        by_technology=by_technology,
    )
