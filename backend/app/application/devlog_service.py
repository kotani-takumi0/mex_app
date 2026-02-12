"""開発ログ管理サービス"""
import logging
from dataclasses import dataclass, field

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import DevLogEntry, Project
from app.domain.security.secret_detector import get_secret_detector

logger = logging.getLogger(__name__)


@dataclass
class DevLogCreate:
    """開発ログ作成入力"""
    source: str = "manual"
    entry_type: str = ""
    summary: str = ""
    detail: str | None = None
    technologies: list[str] = field(default_factory=list)
    ai_tool: str | None = None
    metadata: dict | None = None


@dataclass
class DevLogUpdate:
    """開発ログ更新入力"""
    source: str | None = None
    entry_type: str | None = None
    summary: str | None = None
    detail: str | None = None
    technologies: list[str] | None = None
    ai_tool: str | None = None
    metadata: dict | None = None


@dataclass
class DevLogSummary:
    """開発ログ概要（一覧用）"""
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


class DevLogService:
    """開発ログ管理サービス"""

    def list_entries(self, user_id: str, project_id: str, limit: int | None = None) -> tuple[list[DevLogSummary], int]:
        db = SessionLocal()
        try:
            self._ensure_project(db, user_id, project_id)

            query = (
                db.query(DevLogEntry)
                .filter(DevLogEntry.project_id == project_id, DevLogEntry.user_id == user_id)
                .order_by(DevLogEntry.created_at.desc())
            )
            total = query.count()
            if limit:
                query = query.limit(limit)
            entries = query.all()

            return [self._to_summary(e) for e in entries], total
        finally:
            db.close()

    def create_entry(self, user_id: str, project_id: str, data: DevLogCreate) -> DevLogSummary:
        db = SessionLocal()
        try:
            self._ensure_project(db, user_id, project_id)

            # シークレット検出・マスキング
            detector = get_secret_detector()
            masked_summary = detector.mask(data.summary)
            masked_detail = detector.mask(data.detail) if data.detail else data.detail

            if masked_summary != data.summary or masked_detail != data.detail:
                logger.warning(
                    "シークレットを検出しマスキングしました (user_id=%s, project_id=%s)",
                    user_id, project_id,
                )

            entry = DevLogEntry(
                project_id=project_id,
                user_id=user_id,
                source=data.source or "manual",
                entry_type=data.entry_type,
                summary=masked_summary,
                detail=masked_detail,
                technologies=data.technologies,
                ai_tool=data.ai_tool,
                metadata_=(data.metadata or {}),
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return self._to_summary(entry)
        finally:
            db.close()

    def update_entry(self, user_id: str, entry_id: str, data: DevLogUpdate) -> DevLogSummary:
        db = SessionLocal()
        try:
            entry = (
                db.query(DevLogEntry)
                .filter(DevLogEntry.id == entry_id, DevLogEntry.user_id == user_id)
                .first()
            )
            if entry is None:
                raise ValueError("DevLog entry not found")

            # シークレット検出・マスキング（create_entryと同様に適用）
            detector = get_secret_detector()

            if data.source is not None:
                entry.source = data.source
            if data.entry_type is not None:
                entry.entry_type = data.entry_type
            if data.summary is not None:
                masked_summary = detector.mask(data.summary)
                if masked_summary != data.summary:
                    logger.warning(
                        "シークレットを検出しマスキングしました (user_id=%s, entry_id=%s, field=summary)",
                        user_id, entry_id,
                    )
                entry.summary = masked_summary
            if data.detail is not None:
                masked_detail = detector.mask(data.detail)
                if masked_detail != data.detail:
                    logger.warning(
                        "シークレットを検出しマスキングしました (user_id=%s, entry_id=%s, field=detail)",
                        user_id, entry_id,
                    )
                entry.detail = masked_detail
            if data.technologies is not None:
                entry.technologies = data.technologies
            if data.ai_tool is not None:
                entry.ai_tool = data.ai_tool
            if data.metadata is not None:
                entry.metadata_ = data.metadata

            db.commit()
            db.refresh(entry)
            return self._to_summary(entry)
        finally:
            db.close()

    def delete_entry(self, user_id: str, entry_id: str) -> None:
        db = SessionLocal()
        try:
            entry = (
                db.query(DevLogEntry)
                .filter(DevLogEntry.id == entry_id, DevLogEntry.user_id == user_id)
                .first()
            )
            if entry is None:
                raise ValueError("DevLog entry not found")
            db.delete(entry)
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _ensure_project(db, user_id: str, project_id: str) -> None:
        project = (
            db.query(Project)
            .filter(Project.id == project_id, Project.user_id == user_id)
            .first()
        )
        if project is None:
            raise ValueError("Project not found")

    @staticmethod
    def _to_summary(entry: DevLogEntry) -> DevLogSummary:
        return DevLogSummary(
            id=entry.id,
            project_id=entry.project_id,
            source=entry.source,
            entry_type=entry.entry_type,
            summary=entry.summary,
            detail=entry.detail,
            technologies=entry.technologies or [],
            ai_tool=entry.ai_tool,
            created_at=entry.created_at.isoformat() if entry.created_at else "",
            metadata=entry.metadata_ or {},
        )
