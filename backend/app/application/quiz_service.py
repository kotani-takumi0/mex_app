"""理解度チェック（クイズ）サービス"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.question.question_generator import QuestionGenerator
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import DevLogEntry, Project, QuizQuestion, QuizAttempt, SkillScore


@dataclass
class QuizGenerateRequest:
    """クイズ生成リクエスト"""
    count: int = 5
    difficulty: str = "medium"
    technologies: list[str] = field(default_factory=list)


@dataclass
class QuizQuestionSummary:
    """クイズ問題（回答前）"""
    id: str
    technology: str
    question: str
    options: list[str]
    difficulty: str
    devlog_entry_id: str | None


@dataclass
class ScoreUpdate:
    """スコア更新結果"""
    technology: str
    previous_score: float
    new_score: float
    total_questions: int
    correct_answers: int


@dataclass
class QuizAnswerResult:
    """クイズ回答結果"""
    is_correct: bool
    correct_answer: int
    explanation: str
    score_update: ScoreUpdate


@dataclass
class SkillScoreSummary:
    """スキルスコア概要"""
    technology: str
    score: float
    total_questions: int
    correct_answers: int
    last_assessed_at: str | None


class QuizService:
    """クイズ生成・回答・スコア管理サービス"""

    def __init__(self, generator: QuestionGenerator | None = None):
        self._generator = generator or QuestionGenerator()

    async def generate_quiz(self, user_id: str, project_id: str, request: QuizGenerateRequest) -> list[QuizQuestionSummary]:
        db = SessionLocal()
        try:
            project = (
                db.query(Project)
                .filter(Project.id == project_id, Project.user_id == user_id)
                .first()
            )
            if project is None:
                raise ValueError("Project not found")

            devlog_entries = (
                db.query(DevLogEntry)
                .filter(DevLogEntry.project_id == project_id, DevLogEntry.user_id == user_id)
                .order_by(DevLogEntry.created_at.desc())
                .limit(100)
                .all()
            )

            if not devlog_entries:
                raise ValueError("DevLog entries not found")

            if request.technologies:
                technologies = request.technologies
            else:
                technologies = self._collect_technologies(devlog_entries)

            if not technologies:
                raise ValueError("Technologies not found")

            devlog_payload = [
                {
                    "id": e.id,
                    "entry_type": e.entry_type,
                    "summary": e.summary,
                    "technologies": e.technologies or [],
                }
                for e in devlog_entries
            ]

            generated = await self._generator.generate_questions(
                devlog_entries=devlog_payload,
                technologies=technologies,
                count=request.count,
                difficulty=request.difficulty,
            )

            entry_by_tech = self._map_entry_by_technology(devlog_entries)

            saved_questions: list[QuizQuestion] = []
            for q in generated:
                devlog_entry_id = entry_by_tech.get(q.technology.lower())
                record = QuizQuestion(
                    project_id=project_id,
                    user_id=user_id,
                    devlog_entry_id=devlog_entry_id,
                    technology=q.technology,
                    question=q.question,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    difficulty=q.difficulty,
                )
                db.add(record)
                saved_questions.append(record)

            db.commit()
            for record in saved_questions:
                db.refresh(record)

            return [self._to_summary(q) for q in saved_questions]
        finally:
            db.close()

    def get_questions(self, user_id: str, project_id: str) -> list[QuizQuestionSummary]:
        db = SessionLocal()
        try:
            questions = (
                db.query(QuizQuestion)
                .filter(QuizQuestion.project_id == project_id, QuizQuestion.user_id == user_id)
                .order_by(QuizQuestion.created_at.desc())
                .all()
            )
            return [self._to_summary(q) for q in questions]
        finally:
            db.close()

    def answer_question(
        self,
        user_id: str,
        question_id: str,
        selected_answer: int,
        time_spent_seconds: int | None = None,
    ) -> QuizAnswerResult:
        db = SessionLocal()
        try:
            question = (
                db.query(QuizQuestion)
                .filter(QuizQuestion.id == question_id, QuizQuestion.user_id == user_id)
                .first()
            )
            if question is None:
                raise ValueError("Quiz question not found")

            is_correct = selected_answer == question.correct_answer

            attempt = QuizAttempt(
                quiz_question_id=question.id,
                user_id=user_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                time_spent_seconds=time_spent_seconds,
            )
            db.add(attempt)

            score_update = self._update_skill_score(db, user_id, question.technology, is_correct)

            db.commit()

            return QuizAnswerResult(
                is_correct=is_correct,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                score_update=score_update,
            )
        finally:
            db.close()

    def get_skill_scores(self, user_id: str) -> list[SkillScoreSummary]:
        db = SessionLocal()
        try:
            scores = (
                db.query(SkillScore)
                .filter(SkillScore.user_id == user_id)
                .order_by(SkillScore.score.desc())
                .all()
            )
            return [
                SkillScoreSummary(
                    technology=s.technology,
                    score=s.score,
                    total_questions=s.total_questions,
                    correct_answers=s.correct_answers,
                    last_assessed_at=s.last_assessed_at.isoformat() if s.last_assessed_at else None,
                )
                for s in scores
            ]
        finally:
            db.close()

    @staticmethod
    def _collect_technologies(entries: list[DevLogEntry]) -> list[str]:
        tech_set: list[str] = []
        for entry in entries:
            for tech in entry.technologies or []:
                if tech not in tech_set:
                    tech_set.append(tech)
        return tech_set

    @staticmethod
    def _map_entry_by_technology(entries: list[DevLogEntry]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for entry in entries:
            for tech in entry.technologies or []:
                key = tech.lower()
                if key not in mapping:
                    mapping[key] = entry.id
        return mapping

    @staticmethod
    def _to_summary(question: QuizQuestion) -> QuizQuestionSummary:
        return QuizQuestionSummary(
            id=question.id,
            technology=question.technology,
            question=question.question,
            options=question.options,
            difficulty=question.difficulty,
            devlog_entry_id=question.devlog_entry_id,
        )

    @staticmethod
    def _update_skill_score(db, user_id: str, technology: str, is_correct: bool) -> ScoreUpdate:
        score = (
            db.query(SkillScore)
            .filter(SkillScore.user_id == user_id, SkillScore.technology == technology)
            .first()
        )

        if score is None:
            score = SkillScore(
                user_id=user_id,
                technology=technology,
                score=0.0,
                total_questions=0,
                correct_answers=0,
            )
            db.add(score)
            db.flush()

        previous_score = score.score
        score.total_questions += 1
        if is_correct:
            score.correct_answers += 1

        score.score = round((score.correct_answers / score.total_questions) * 100, 1)
        score.last_assessed_at = datetime.now(timezone.utc)

        return ScoreUpdate(
            technology=technology,
            previous_score=previous_score,
            new_score=score.score,
            total_questions=score.total_questions,
            correct_answers=score.correct_answers,
        )
