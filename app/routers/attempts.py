"""
Student Attempts API Router

학생 시도 기록 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.repositories.student_attempt_repository import StudentAttemptRepository

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


# Pydantic 모델
class CreateAttemptRequest(BaseModel):
    student_id: str
    question_id: str
    concept: str
    is_correct: bool
    response_time_ms: Optional[int] = None


class AttemptResponse(BaseModel):
    id: int
    student_id: str
    question_id: str
    concept: str
    is_correct: bool
    response_time_ms: Optional[int]
    attempted_at: datetime

    class Config:
        from_attributes = True


class AttemptsListResponse(BaseModel):
    student_id: str
    concept: str
    attempts: List[dict]


# 의존성
def get_repository(db: AsyncSession = Depends(get_db)) -> StudentAttemptRepository:
    """StudentAttemptRepository 인스턴스 생성"""
    return StudentAttemptRepository(db)


# API 엔드포인트
@router.post("", response_model=AttemptResponse, status_code=201)
async def create_attempt(
    request: CreateAttemptRequest,
    repo: StudentAttemptRepository = Depends(get_repository)
):
    """
    새로운 시도 기록 생성

    Args:
        request: 시도 기록 데이터

    Returns:
        생성된 시도 기록
    """
    attempt = await repo.create_attempt(
        student_id=request.student_id,
        question_id=request.question_id,
        concept=request.concept,
        is_correct=request.is_correct,
        response_time_ms=request.response_time_ms
    )

    return attempt


@router.get("/{student_id}/{concept}", response_model=AttemptsListResponse)
async def get_student_attempts(
    student_id: str,
    concept: str,
    limit: Optional[int] = None,
    repo: StudentAttemptRepository = Depends(get_repository)
):
    """
    학생의 특정 개념 시도 기록 조회

    Args:
        student_id: 학생 ID
        concept: 개념명
        limit: 최대 반환 개수

    Returns:
        시도 기록 리스트
    """
    attempts = await repo.get_by_concept(student_id, concept)

    if limit is not None:
        attempts = attempts[:limit]

    # JSON 직렬화 가능한 형태로 변환
    attempts_data = [
        {
            "id": attempt.id,
            "question_id": attempt.question_id,
            "is_correct": attempt.is_correct,
            "response_time_ms": attempt.response_time_ms,
            "attempted_at": attempt.attempted_at.isoformat()
        }
        for attempt in attempts
    ]

    return AttemptsListResponse(
        student_id=student_id,
        concept=concept,
        attempts=attempts_data
    )


@router.delete("/{attempt_id}", status_code=204)
async def delete_attempt(
    attempt_id: int,
    repo: StudentAttemptRepository = Depends(get_repository)
):
    """
    시도 기록 삭제

    Args:
        attempt_id: 시도 기록 ID

    Returns:
        204 No Content
    """
    success = await repo.delete_attempt(attempt_id)

    if not success:
        raise HTTPException(status_code=404, detail="Attempt not found")

    return None
