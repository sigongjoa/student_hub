"""
Exam Preparation Service

시험 준비 워크플로우를 구현합니다.
데이터 플로우: Node 0 → Node 6 (학교 정보) → Node 4 (약점) → Node 2 (연습 문제) → 2주 계획
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.mcp.manager import MCPClientManager
from app.models.workflow_session import WorkflowSession

logger = logging.getLogger(__name__)


@dataclass
class ExamPrepRequest:
    """시험 준비 요청"""
    student_id: str
    exam_date: str  # YYYY-MM-DD
    school_id: str
    curriculum_paths: List[str]


@dataclass
class DailyTask:
    """일일 학습 태스크"""
    day_number: int
    date: str  # YYYY-MM-DD
    concepts_to_review: List[str]
    practice_problems: List[dict]  # Question 객체 리스트
    anki_reviews: int


@dataclass
class ExamPrepResult:
    """시험 준비 결과"""
    workflow_id: str
    two_week_plan: List[DailyTask]
    practice_problems: List[dict]
    focus_concepts: List[str]  # 집중 개념 (약점)
    mock_exam_pdf_url: str


class ExamPrepService:
    """시험 준비 워크플로우 서비스"""

    def __init__(self, mcp: MCPClientManager, db: AsyncSession):
        self.mcp = mcp
        self.db = db

    async def prepare_exam(
        self,
        request: ExamPrepRequest
    ) -> ExamPrepResult:
        """
        시험 준비 워크플로우

        Steps:
        1. 학교 시험 범위 조회 (Node 6)
        2. 학생 약점 개념 식별 (Node 4)
        3. 연습 문제 추천 (Node 2)
        4. 2주 학습 플랜 생성
        5. 모의고사 PDF 생성 (Node 5)
        6. 워크플로우 세션 생성
        """
        logger.info(f"Starting exam preparation for student {request.student_id}, exam: {request.exam_date}")

        # 시험까지 남은 일수 계산
        exam_datetime = datetime.strptime(request.exam_date, "%Y-%m-%d")
        days_until_exam = (exam_datetime - datetime.now()).days
        days_until_exam = max(7, min(days_until_exam, 14))  # 7-14일 범위

        # Step 1: 학교 시험 범위 조회 (Node 6)
        exam_scope_response = await self.mcp.call("school-info", "get_exam_scope", {
            "school_id": request.school_id,
            "curriculum_paths": request.curriculum_paths
        })
        exam_scope = exam_scope_response.get("exam_scope", {})
        exam_topics = exam_scope.get("topics", [])

        # Step 2: 학생 약점 개념 식별 (Node 4)
        weak_concepts_response = await self.mcp.call("lab-node", "get_weak_concepts", {
            "student_id": request.student_id,
            "curriculum_paths": request.curriculum_paths
        })
        weak_concepts_data = weak_concepts_response.get("weak_concepts", [])
        focus_concepts = [wc["concept"] for wc in weak_concepts_data]

        logger.info(f"Focus concepts (weak): {focus_concepts}")

        # Step 3: 연습 문제 추천 (Node 2)
        # 약점 개념 위주 + 전체 범위 복습
        all_practice_problems = []

        for concept in exam_topics:
            is_weak = concept in focus_concepts
            question_count = 15 if is_weak else 10  # 약점 개념은 더 많은 문제

            questions_response = await self.mcp.call("q-dna", "recommend_questions", {
                "student_id": request.student_id,
                "count": question_count,
                "curriculum_path": request.curriculum_paths[0],
                "target_concept": concept,
                "difficulty_mix": True
            })

            questions = questions_response.get("questions", [])
            all_practice_problems.extend(questions)

        logger.info(f"Total practice problems: {len(all_practice_problems)}")

        # Step 4: 2주 학습 플랜 생성
        two_week_plan = self._generate_study_plan(
            days_until_exam=days_until_exam,
            focus_concepts=focus_concepts,
            all_topics=exam_topics,
            practice_problems=all_practice_problems
        )

        # Step 5: 모의고사 PDF 생성 (Node 5)
        mock_exam_response = await self.mcp.call("q-metrics", "generate_mock_exam", {
            "student_id": request.student_id,
            "curriculum_paths": request.curriculum_paths,
            "question_count": 25,
            "difficulty_distribution": exam_scope.get("difficulty_distribution", {})
        })
        mock_exam_pdf_url = mock_exam_response.get("pdf_url", "")

        # Step 6: 워크플로우 세션 생성
        workflow_session = WorkflowSession(
            student_id=request.student_id,
            workflow_type="exam_prep",
            status="in_progress",
            workflow_metadata={
                "exam_date": request.exam_date,
                "school_id": request.school_id,
                "curriculum_paths": request.curriculum_paths,
                "focus_concepts": focus_concepts,
                "days_until_exam": days_until_exam,
                "total_problems": len(all_practice_problems),
                "mock_exam_pdf_url": mock_exam_pdf_url,
                "created_at": datetime.now().isoformat()
            }
        )

        self.db.add(workflow_session)
        await self.db.commit()
        await self.db.refresh(workflow_session)

        logger.info(f"Created exam prep workflow {workflow_session.workflow_id}")

        return ExamPrepResult(
            workflow_id=workflow_session.workflow_id,
            two_week_plan=two_week_plan,
            practice_problems=all_practice_problems,
            focus_concepts=focus_concepts,
            mock_exam_pdf_url=mock_exam_pdf_url
        )

    def _generate_study_plan(
        self,
        days_until_exam: int,
        focus_concepts: List[str],
        all_topics: List[str],
        practice_problems: List[dict]
    ) -> List[DailyTask]:
        """
        2주 학습 플랜 생성

        패턴:
        - Day 1-7: 약점 집중 공략 (새로운 개념)
        - Day 8-11: 전범위 복습
        - Day 12-13: 모의고사
        - Day 14: 최종 점검 (Anki 위주)
        """
        daily_tasks = []
        problem_pool = practice_problems.copy()
        base_date = datetime.now()

        for day_num in range(1, days_until_exam + 1):
            current_date = base_date + timedelta(days=day_num - 1)

            # 각 단계별 전략
            if day_num <= 7:
                # Phase 1: 약점 집중 공략
                concepts = focus_concepts[:2] if focus_concepts else all_topics[:2]
                problem_count = 8
                anki_count = day_num  # 점진적 증가

            elif day_num <= 11:
                # Phase 2: 전범위 복습
                concepts = all_topics[:3]
                problem_count = 10
                anki_count = 5

            elif day_num <= 13:
                # Phase 3: 모의고사
                concepts = ["모의고사"]
                problem_count = 12  # 더 많은 문제
                anki_count = 8

            else:
                # Phase 4: 최종 점검
                concepts = focus_concepts[:1] if focus_concepts else all_topics[:1]
                problem_count = 5  # 가볍게
                anki_count = 10  # Anki 집중

            # 문제 할당
            day_problems = []
            if problem_pool:
                allocated = min(problem_count, len(problem_pool))
                day_problems = problem_pool[:allocated]
                problem_pool = problem_pool[allocated:]

            daily_task = DailyTask(
                day_number=day_num,
                date=current_date.strftime("%Y-%m-%d"),
                concepts_to_review=concepts,
                practice_problems=day_problems,
                anki_reviews=anki_count
            )
            daily_tasks.append(daily_task)

        return daily_tasks

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
            "metadata": session.workflow_metadata
        }
