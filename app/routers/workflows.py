"""
Workflow API Router

Phase 1-4 워크플로우 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime, date

from app.db.session import get_db
from app.mcp.manager import MCPClientManager
from app.services.weekly_diagnostic_service import (
    WeeklyDiagnosticService,
    WeeklyDiagnosticRequest as ServiceWeeklyRequest,
    Question as ServiceQuestion
)
from app.services.error_review_service import (
    ErrorReviewService,
    ErrorReviewRequest as ServiceErrorRequest
)
from app.services.learning_path_service import (
    LearningPathService,
    LearningPathRequest as ServiceLearningRequest
)
from app.services.exam_prep_service import (
    ExamPrepService,
    ExamPrepRequest as ServiceExamRequest
)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


# ============================================================================
# Pydantic Request/Response Models
# ============================================================================

# Weekly Diagnostic Models
class WeeklyDiagnosticRequest(BaseModel):
    student_id: str = Field(..., description="학생 ID")
    curriculum_path: str = Field(..., description="커리큘럼 경로")
    include_weak_concepts: bool = Field(True, description="약점 개념 포함 여부")


class Question(BaseModel):
    id: str
    content: str
    difficulty: str
    concepts: List[str]


class WeeklyDiagnosticResponse(BaseModel):
    workflow_id: str
    session_id: int
    questions: List[Question]
    weak_concepts: List[str]
    total_estimated_time_minutes: int
    started_at: str


# Error Review Models
class ErrorReviewRequest(BaseModel):
    student_id: str = Field(..., description="학생 ID")
    question_id: str = Field(..., description="문제 ID")
    student_answer: str = Field(..., description="학생 답변")
    correct_answer: str = Field(..., description="정답")


class ErrorAnalysis(BaseModel):
    misconception: str
    root_cause: str
    related_concepts: List[str]


class ErrorReviewResponse(BaseModel):
    error_note_id: str
    next_review_date: str
    anki_interval_days: int
    analysis: ErrorAnalysis


# Learning Path Models
class LearningPathRequest(BaseModel):
    student_id: str = Field(..., description="학생 ID")
    target_concept: str = Field(..., description="목표 개념")
    days: int = Field(..., description="학습 기간(일)")


class PathNode(BaseModel):
    concept: str
    order: int
    estimated_hours: int
    prerequisites: List[str]


class LearningPathResponse(BaseModel):
    workflow_id: str
    learning_path: List[PathNode]
    total_estimated_hours: int
    daily_tasks: Dict[str, int]


# Exam Prep Models
class ExamPrepRequest(BaseModel):
    student_id: str = Field(..., description="학생 ID")
    exam_date: str = Field(..., description="시험 날짜 (YYYY-MM-DD)")
    school_id: str = Field(..., description="학교 ID")
    curriculum_paths: List[str] = Field(..., description="커리큘럼 경로 목록")


class DailyTaskResponse(BaseModel):
    day_number: int
    date: str
    concepts_to_review: List[str]
    practice_problems: List[Question]
    anki_reviews: int


class ExamPrepResponse(BaseModel):
    workflow_id: str
    two_week_plan: List[DailyTaskResponse]
    practice_problems: List[Question]
    focus_concepts: List[str]


# ============================================================================
# Dependencies
# ============================================================================

def get_mcp_manager() -> MCPClientManager:
    """MCP Client Manager 싱글톤"""
    return MCPClientManager()


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/weekly-diagnostic", response_model=WeeklyDiagnosticResponse)
async def weekly_diagnostic(
    request: WeeklyDiagnosticRequest,
    db: AsyncSession = Depends(get_db),
    mcp: MCPClientManager = Depends(get_mcp_manager)
):
    """
    주간 진단 워크플로우

    학생의 최근 학습 활동을 분석하여 약점 개념을 식별하고
    맞춤형 문제를 추천합니다.

    **데이터 플로우**:
    1. Node 4 (Lab Node): 최근 학습 개념 조회
    2. Node 2 (Q-DNA): BKT 숙련도 계산
    3. 약점 개념 식별 (숙련도 < 0.6)
    4. Node 2 (Q-DNA): IRT 기반 문제 추천
    """
    try:
        service = WeeklyDiagnosticService(mcp, db)
        service_request = ServiceWeeklyRequest(
            student_id=request.student_id,
            curriculum_path=request.curriculum_path,
            include_weak_concepts=request.include_weak_concepts
        )

        result = await service.start_diagnostic(service_request)

        # Convert dataclass to response model
        return WeeklyDiagnosticResponse(
            workflow_id=result.workflow_id,
            session_id=result.session_id,
            questions=[
                Question(
                    id=q.id,
                    content=q.content,
                    difficulty=q.difficulty,
                    concepts=q.concepts
                )
                for q in result.questions
            ],
            weak_concepts=result.weak_concepts,
            total_estimated_time_minutes=result.total_estimated_time_minutes,
            started_at=result.started_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weekly diagnostic failed: {str(e)}")


@router.post("/error-review", response_model=ErrorReviewResponse)
async def error_review(
    request: ErrorReviewRequest,
    db: AsyncSession = Depends(get_db),
    mcp: MCPClientManager = Depends(get_mcp_manager)
):
    """
    오답 복습 워크플로우

    학생의 오답을 분석하여 오개념을 진단하고
    Anki 알고리즘 기반 복습 스케줄을 생성합니다.

    **데이터 플로우**:
    1. Node 4 (Lab Node): 오답 감지
    2. Node 7 (Error Note): 오답 노트 생성
    3. Anki SM-2: 복습 스케줄링
    """
    try:
        service = ErrorReviewService(mcp, db)
        service_request = ServiceErrorRequest(
            student_id=request.student_id,
            question_id=request.question_id,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer
        )

        result = await service.start_error_review(service_request)

        return ErrorReviewResponse(
            error_note_id=result.error_note_id,
            next_review_date=result.next_review_date.isoformat(),
            anki_interval_days=result.anki_interval_days,
            analysis=ErrorAnalysis(
                misconception=result.analysis.misconception,
                root_cause=result.analysis.root_cause,
                related_concepts=result.analysis.related_concepts
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error review failed: {str(e)}")


@router.post("/learning-path", response_model=LearningPathResponse)
async def learning_path(
    request: LearningPathRequest,
    db: AsyncSession = Depends(get_db),
    mcp: MCPClientManager = Depends(get_mcp_manager)
):
    """
    개인화 학습 경로 생성 워크플로우

    목표 개념까지의 최적 학습 순서를 생성합니다.
    선수지식 그래프와 Topological Sort를 사용합니다.

    **데이터 플로우**:
    1. Node 4 (Lab Node): 학생 히트맵 조회
    2. Node 1 (Logic Engine): 선수지식 그래프 조회
    3. Topological Sort: 최적 학습 순서 결정
    4. AI 학습 시간 추정
    """
    try:
        service = LearningPathService(mcp, db)
        service_request = ServiceLearningRequest(
            student_id=request.student_id,
            target_concept=request.target_concept,
            days=request.days
        )

        result = await service.generate_learning_path(service_request)

        return LearningPathResponse(
            workflow_id=result.workflow_id,
            learning_path=[
                PathNode(
                    concept=node.concept,
                    order=node.order,
                    estimated_hours=node.estimated_hours,
                    prerequisites=node.prerequisites
                )
                for node in result.learning_path
            ],
            total_estimated_hours=result.total_estimated_hours,
            daily_tasks=result.daily_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning path generation failed: {str(e)}")


@router.post("/exam-prep", response_model=ExamPrepResponse)
async def exam_prep(
    request: ExamPrepRequest,
    db: AsyncSession = Depends(get_db),
    mcp: MCPClientManager = Depends(get_mcp_manager)
):
    """
    시험 준비 워크플로우

    시험 2주 전 맞춤형 학습 계획을 생성합니다.
    4-Phase 전략으로 약점 개념 우선 학습 후 실전 연습을 진행합니다.

    **데이터 플로우**:
    1. Node 6 (School Info): 학교 정보 및 시험 범위 조회
    2. Node 4 (Lab Node): 약점 개념 분석
    3. Node 2 (Q-DNA): 연습 문제 생성
    4. 2주 학습 플랜 생성
    """
    try:
        service = ExamPrepService(mcp, db)
        service_request = ServiceExamRequest(
            student_id=request.student_id,
            exam_date=request.exam_date,
            school_id=request.school_id,
            curriculum_paths=request.curriculum_paths
        )

        result = await service.prepare_exam(service_request)

        return ExamPrepResponse(
            workflow_id=result.workflow_id,
            two_week_plan=[
                DailyTaskResponse(
                    day_number=task.day_number,
                    date=task.date,
                    concepts_to_review=task.concepts_to_review,
                    practice_problems=[
                        Question(
                            id=p["id"],
                            content=p["content"],
                            difficulty=p["difficulty"],
                            concepts=p["concepts"]
                        )
                        for p in task.practice_problems
                    ],
                    anki_reviews=task.anki_reviews
                )
                for task in result.two_week_plan
            ],
            practice_problems=[
                Question(
                    id=q["id"],
                    content=q["content"],
                    difficulty=q["difficulty"],
                    concepts=q["concepts"]
                )
                for q in result.practice_problems
            ],
            focus_concepts=result.focus_concepts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exam preparation failed: {str(e)}")
