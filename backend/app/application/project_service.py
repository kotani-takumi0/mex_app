"""プロジェクト管理サービス"""

from dataclasses import dataclass, field

from app.infrastructure.database.models import DevLogEntry, Project, QuizAttempt, QuizQuestion
from app.infrastructure.database.session import SessionLocal


@dataclass
class ProjectCreate:
    """プロジェクト作成入力"""

    title: str
    description: str | None = None
    technologies: list[str] = field(default_factory=list)
    repository_url: str | None = None
    demo_url: str | None = None
    status: str = "in_progress"
    is_public: bool = False


@dataclass
class ProjectUpdate:
    """プロジェクト更新入力"""

    title: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    repository_url: str | None = None
    demo_url: str | None = None
    status: str | None = None
    is_public: bool | None = None


@dataclass
class ProjectSummary:
    """プロジェクト情報（一覧・詳細用）"""

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


class ProjectService:
    """プロジェクト管理サービス"""

    def list_projects(self, user_id: str) -> list[ProjectSummary]:
        db = SessionLocal()
        try:
            projects = (
                db.query(Project)
                .filter(Project.user_id == user_id)
                .order_by(Project.updated_at.desc())
                .all()
            )
            return [self._to_summary(db, p, user_id) for p in projects]
        finally:
            db.close()

    def get_project(self, user_id: str, project_id: str) -> ProjectSummary:
        db = SessionLocal()
        try:
            project = self._get_project(db, user_id, project_id)
            return self._to_summary(db, project, user_id)
        finally:
            db.close()

    def create_project(self, user_id: str, data: ProjectCreate) -> ProjectSummary:
        db = SessionLocal()
        try:
            project = Project(
                user_id=user_id,
                title=data.title,
                description=data.description,
                technologies=data.technologies,
                repository_url=data.repository_url,
                demo_url=data.demo_url,
                status=data.status,
                is_public=data.is_public,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            return self._to_summary(db, project, user_id)
        finally:
            db.close()

    def update_project(self, user_id: str, project_id: str, data: ProjectUpdate) -> ProjectSummary:
        db = SessionLocal()
        try:
            project = self._get_project(db, user_id, project_id)

            if data.title is not None:
                project.title = data.title
            if data.description is not None:
                project.description = data.description
            if data.technologies is not None:
                project.technologies = data.technologies
            if data.repository_url is not None:
                project.repository_url = data.repository_url
            if data.demo_url is not None:
                project.demo_url = data.demo_url
            if data.status is not None:
                project.status = data.status
            if data.is_public is not None:
                project.is_public = data.is_public

            db.commit()
            db.refresh(project)
            return self._to_summary(db, project, user_id)
        finally:
            db.close()

    def delete_project(self, user_id: str, project_id: str) -> None:
        db = SessionLocal()
        try:
            project = self._get_project(db, user_id, project_id)
            db.delete(project)
            db.commit()
        finally:
            db.close()

    def _get_project(self, db, user_id: str, project_id: str) -> Project:
        project = (
            db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
        )
        if project is None:
            raise ValueError("Project not found")
        return project

    def _to_summary(self, db, project: Project, user_id: str) -> ProjectSummary:
        devlog_count = db.query(DevLogEntry).filter(DevLogEntry.project_id == project.id).count()

        quiz_score = self._calculate_quiz_score(db, project.id, user_id)

        return ProjectSummary(
            id=project.id,
            title=project.title,
            description=project.description,
            technologies=project.technologies or [],
            repository_url=project.repository_url,
            demo_url=project.demo_url,
            status=project.status,
            is_public=project.is_public,
            devlog_count=devlog_count,
            quiz_score=quiz_score,
            created_at=project.created_at.isoformat() if project.created_at else "",
            updated_at=project.updated_at.isoformat() if project.updated_at else "",
        )

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
