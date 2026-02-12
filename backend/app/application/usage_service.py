"""ダッシュボード統計サービス"""

from dataclasses import dataclass

from app.infrastructure.database.models import (
    DevLogEntry,
    Project,
    QuizAttempt,
    QuizQuestion,
    SkillScore,
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
    total_quiz_answered: int
    overall_score: float


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
    quiz_score: float | None
    created_at: str
    updated_at: str


@dataclass
class DashboardSkill:
    technology: str
    score: float
    total_questions: int
    correct_answers: int
    last_assessed_at: str | None


@dataclass
class DashboardData:
    user: DashboardUser
    stats: DashboardStats
    recent_projects: list[DashboardProject]
    top_skills: list[DashboardSkill]


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
            total_quiz_answered = (
                db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).count()
            )

            skill_scores = (
                db.query(SkillScore)
                .filter(SkillScore.user_id == user_id)
                .order_by(SkillScore.score.desc())
                .all()
            )
            if skill_scores:
                overall_score = round(sum(s.score for s in skill_scores) / len(skill_scores), 1)
            else:
                overall_score = 0.0

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
                    quiz_score=self._calculate_quiz_score(db, p.id, user_id),
                    created_at=p.created_at.isoformat() if p.created_at else "",
                    updated_at=p.updated_at.isoformat() if p.updated_at else "",
                )
                for p in recent_projects
            ]

            top_skills = [
                DashboardSkill(
                    technology=s.technology,
                    score=s.score,
                    total_questions=s.total_questions,
                    correct_answers=s.correct_answers,
                    last_assessed_at=s.last_assessed_at.isoformat() if s.last_assessed_at else None,
                )
                for s in skill_scores[:3]
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
                    total_quiz_answered=total_quiz_answered,
                    overall_score=overall_score,
                ),
                recent_projects=recent_project_summaries,
                top_skills=top_skills,
            )
        finally:
            db.close()

    @staticmethod
    def _calculate_quiz_score(db, project_id: str, user_id: str) -> float | None:
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
