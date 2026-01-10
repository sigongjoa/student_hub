"""
Error Review Service

오답 복습 워크플로우를 구현합니다.
데이터 플로우: Node 0 → Node 4 (오답 감지) → Node 7 (오답노트 생성) → Node 7 (Anki 스케줄링)
"""
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.mcp.manager import MCPClientManager
from app.models.workflow_session import WorkflowSession

logger = logging.getLogger(__name__)


@dataclass
class ErrorReviewRequest:
    """오답 복습 요청"""
    student_id: str
    question_id: str
    student_answer: str
    correct_answer: str


@dataclass
class ErrorAnalysis:
    """오답 분석"""
    misconception: str  # 오개념
    root_cause: str  # 근본 원인
    related_concepts: List[str]  # 관련 개념


@dataclass
class ErrorReviewResult:
    """오답 복습 결과"""
    error_note_id: str
    next_review_date: datetime
    anki_interval_days: int
    analysis: ErrorAnalysis


class ErrorReviewService:
    """오답 복습 워크플로우 서비스"""

    def __init__(self, mcp: MCPClientManager, db: AsyncSession):
        self.mcp = mcp
        self.db = db

    async def start_error_review(
        self,
        request: ErrorReviewRequest
    ) -> ErrorReviewResult:
        """
        오답 복습 워크플로우 시작

        Steps:
        1. 문제 DNA 가져오기 (Node 2)
        2. 오답노트 생성 (Node 7)
        3. Anki 스케줄 계산 (Node 7)
        4. 워크플로우 세션 생성 (completed)
        """
        logger.info(f"Starting error review for student {request.student_id}, question {request.question_id}")

        # Step 1: 문제 DNA 가져오기 (Node 2)
        question_dna = await self.mcp.call("q-dna", "get_question_dna", {
            "question_id": request.question_id
        })

        # Step 2: 오답노트 생성 (Node 7)
        error_note_response = await self.mcp.call("error-note", "create_error_note", {
            "student_id": request.student_id,
            "question_id": request.question_id,
            "student_answer": request.student_answer,
            "correct_answer": request.correct_answer,
            "question_dna": question_dna
        })

        error_note_id = error_note_response["error_note_id"]
        analysis_data = error_note_response.get("analysis", {})

        # Step 3: Anki 스케줄 계산 (Node 7 - SuperMemo SM-2)
        anki_schedule = await self.mcp.call("error-note", "calculate_anki_schedule", {
            "error_note_id": error_note_id,
            "student_id": request.student_id,
            "quality": 0  # 첫 오답은 quality 0 (실패)
        })

        next_review_date = datetime.fromisoformat(anki_schedule["next_review_date"])
        interval_days = anki_schedule["interval_days"]

        # 오답 분석 객체 생성
        analysis = ErrorAnalysis(
            misconception=analysis_data.get("misconception", "오개념 분석 중"),
            root_cause=analysis_data.get("root_cause", "근본 원인 분석 중"),
            related_concepts=analysis_data.get("related_concepts", [])
        )

        # Step 4: 워크플로우 세션 생성 (즉시 completed)
        workflow_session = WorkflowSession(
            student_id=request.student_id,
            workflow_type="error_review",
            status="completed",  # 오답 복습은 즉시 완료
            workflow_metadata={
                "error_note_id": error_note_id,
                "question_id": request.question_id,
                "next_review_date": next_review_date.isoformat(),
                "anki_interval_days": interval_days,
                "created_at": datetime.now().isoformat()
            }
        )
        workflow_session.completed_at = datetime.now()

        self.db.add(workflow_session)
        await self.db.commit()
        await self.db.refresh(workflow_session)

        logger.info(f"Created error note {error_note_id} with next review at {next_review_date}")

        # 결과 반환
        return ErrorReviewResult(
            error_note_id=error_note_id,
            next_review_date=next_review_date,
            anki_interval_days=interval_days,
            analysis=analysis
        )

    async def get_student_error_notes(
        self,
        student_id: str,
        limit: int = 20
    ) -> List[dict]:
        """학생의 오답노트 목록 조회"""
        stmt = (
            select(WorkflowSession)
            .where(
                WorkflowSession.student_id == student_id,
                WorkflowSession.workflow_type == "error_review"
            )
            .order_by(WorkflowSession.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        return [
            {
                "error_note_id": session.workflow_metadata.get("error_note_id"),
                "question_id": session.workflow_metadata.get("question_id"),
                "next_review_date": session.workflow_metadata.get("next_review_date"),
                "created_at": session.created_at.isoformat()
            }
            for session in sessions
        ]
