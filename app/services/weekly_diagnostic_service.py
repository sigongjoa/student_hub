"""
Weekly Diagnostic Service

주간 진단 워크플로우를 구현합니다.
데이터 플로우: Node 0 → Node 4 (최근 학습 활동) → Node 2 (BKT 숙련도) → Node 2 (문제 추천)
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
class WeeklyDiagnosticRequest:
    """주간 진단 요청"""
    student_id: str
    curriculum_path: str
    include_weak_concepts: bool = True


@dataclass
class Question:
    """문제 정보"""
    id: str
    content: str
    difficulty: str
    concepts: List[str]


@dataclass
class WeeklyDiagnosticResult:
    """주간 진단 결과"""
    workflow_id: str
    session_id: int
    questions: List[Question]
    weak_concepts: List[str]
    total_estimated_time_minutes: int
    started_at: datetime


class WeeklyDiagnosticService:
    """주간 진단 워크플로우 서비스"""

    def __init__(self, mcp: MCPClientManager, db: AsyncSession):
        self.mcp = mcp
        self.db = db

    async def start_diagnostic(
        self,
        request: WeeklyDiagnosticRequest
    ) -> WeeklyDiagnosticResult:
        """
        주간 진단 워크플로우 시작

        Steps:
        1. 최근 학습 개념 가져오기 (Node 4)
        2. BKT 숙련도 조회 (Node 2)
        3. 약점 개념 식별 (< 0.6)
        4. 문제 추천 (Node 2 - IRT)
        5. 워크플로우 세션 생성
        """
        logger.info(f"Starting weekly diagnostic for student {request.student_id}")

        # Step 1: 최근 학습 개념 가져오기 (Node 4)
        recent_concepts_response = await self.mcp.call("lab-node", "get_recent_concepts", {
            "student_id": request.student_id,
            "curriculum_path": request.curriculum_path,
            "days": 7
        })
        recent_concepts = recent_concepts_response.get("concepts", [])

        # Step 2: BKT 숙련도 조회 (Node 2)
        weak_concepts = []
        if request.include_weak_concepts and recent_concepts:
            mastery_response = await self.mcp.call("q-dna", "get_student_mastery", {
                "student_id": request.student_id,
                "skill_ids": recent_concepts
            })

            # Step 3: 약점 개념 식별 (숙련도 < 0.6)
            weak_concepts = [
                concept for concept, score in mastery_response.items()
                if score < 0.6
            ]
            logger.info(f"Identified weak concepts: {weak_concepts}")

        # Step 4: 문제 추천 (Node 2)
        questions_response = await self.mcp.call("q-dna", "recommend_questions", {
            "student_id": request.student_id,
            "count": 10,
            "curriculum_path": request.curriculum_path,
            "weak_concepts": weak_concepts,
            "weak_ratio": 0.6 if weak_concepts else 0.0
        })

        # 문제 리스트 변환
        questions = [
            Question(
                id=q["id"],
                content=q["content"],
                difficulty=q["difficulty"],
                concepts=q.get("concepts", [])
            )
            for q in questions_response.get("questions", [])
        ]

        # Step 5: 워크플로우 세션 생성
        workflow_session = WorkflowSession(
            student_id=request.student_id,
            workflow_type="weekly_diagnostic",
            status="in_progress",
            workflow_metadata={
                "curriculum_path": request.curriculum_path,
                "weak_concepts": weak_concepts,
                "questions": [{"id": q.id, "difficulty": q.difficulty} for q in questions],
                "started_at": datetime.now().isoformat()
            }
        )

        self.db.add(workflow_session)
        await self.db.commit()
        await self.db.refresh(workflow_session)

        logger.info(f"Created workflow session {workflow_session.workflow_id}")

        # 결과 반환
        return WeeklyDiagnosticResult(
            workflow_id=workflow_session.workflow_id,
            session_id=workflow_session.id,
            questions=questions,
            weak_concepts=weak_concepts,
            total_estimated_time_minutes=len(questions) * 2,  # 문제당 2분
            started_at=datetime.now()
        )

    async def get_workflow_status(self, workflow_id: str) -> Optional[dict]:
        """워크플로우 상태 조회"""
        stmt = select(WorkflowSession).where(WorkflowSession.workflow_id == workflow_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            return None

        return {
            "workflow_id": session.workflow_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "metadata": session.workflow_metadata
        }
