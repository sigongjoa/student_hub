"""
Mastery API Router

학생 숙련도 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, List

from app.db.session import get_db
from app.repositories.student_attempt_repository import StudentAttemptRepository
from app.algorithms.bkt import BayesianKnowledgeTracing
from app.services.mastery_service import MasteryService

router = APIRouter(prefix="/api/mastery", tags=["mastery"])


# Pydantic 모델
class CalculateMasteryRequest(BaseModel):
    student_id: str
    concept: str


class CalculateMasteryResponse(BaseModel):
    student_id: str
    concept: str
    mastery: float


class MasteryProfileResponse(BaseModel):
    student_id: str
    profile: Dict[str, float]


class WeakConcept(BaseModel):
    concept: str
    mastery: float


class WeakConceptsResponse(BaseModel):
    student_id: str
    threshold: float
    weak_concepts: List[WeakConcept]


# 의존성
def get_mastery_service(db: AsyncSession = Depends(get_db)) -> MasteryService:
    """MasteryService 인스턴스 생성"""
    repo = StudentAttemptRepository(db)
    bkt = BayesianKnowledgeTracing()
    return MasteryService(repo, bkt)


# API 엔드포인트
@router.post("/calculate", response_model=CalculateMasteryResponse)
async def calculate_mastery(
    request: CalculateMasteryRequest,
    service: MasteryService = Depends(get_mastery_service)
):
    """
    학생의 개념 숙련도 계산

    Args:
        request: student_id, concept

    Returns:
        숙련도 계산 결과
    """
    mastery = await service.calculate_concept_mastery(
        request.student_id,
        request.concept
    )

    return CalculateMasteryResponse(
        student_id=request.student_id,
        concept=request.concept,
        mastery=mastery
    )


@router.get("/profile/{student_id}", response_model=MasteryProfileResponse)
async def get_mastery_profile(
    student_id: str,
    service: MasteryService = Depends(get_mastery_service)
):
    """
    학생의 전체 숙련도 프로파일 조회

    Args:
        student_id: 학생 ID

    Returns:
        전체 개념별 숙련도 맵
    """
    profile = await service.get_student_mastery_profile(student_id)

    return MasteryProfileResponse(
        student_id=student_id,
        profile=profile
    )


@router.get("/weak-concepts/{student_id}", response_model=WeakConceptsResponse)
async def get_weak_concepts(
    student_id: str,
    threshold: float = 0.5,
    service: MasteryService = Depends(get_mastery_service)
):
    """
    약점 개념 조회

    Args:
        student_id: 학생 ID
        threshold: 약점 판단 임계값 (기본값: 0.5)

    Returns:
        약점 개념 리스트 (개념명과 숙련도 포함)
    """
    # 전체 프로파일 조회
    profile = await service.get_student_mastery_profile(student_id)

    # 약점 개념 필터링 (threshold 미만)
    weak_concepts = [
        WeakConcept(concept=concept, mastery=mastery)
        for concept, mastery in profile.items()
        if mastery < threshold
    ]

    # 숙련도 낮은 순서대로 정렬
    weak_concepts.sort(key=lambda x: x.mastery)

    return WeakConceptsResponse(
        student_id=student_id,
        threshold=threshold,
        weak_concepts=weak_concepts
    )
