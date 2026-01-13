"""
Unit Tests for MasteryService

TDD: 학생 숙련도 계산 서비스 테스트

MasteryService:
- StudentAttemptRepository와 BKT 알고리즘을 통합
- 학생의 개념별 숙련도 계산
- 여러 개념에 대한 숙련도 맵 생성

Target: 100% code coverage
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_concept_mastery_no_attempts(db_session):
    """
    Test: 시도 기록이 없는 개념의 숙련도 계산
    Expected: p_init (초기 숙련도) 반환
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing

    # Given
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing(p_init=0.1)
    service = MasteryService(repo, bkt)

    # When
    mastery = await service.calculate_concept_mastery("student_123", "존재하지_않는_개념")

    # Then
    assert mastery == pytest.approx(0.1, abs=0.01)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_concept_mastery_with_attempts(db_session):
    """
    Test: 시도 기록이 있는 개념의 숙련도 계산
    Expected: BKT로 계산된 숙련도 반환
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    # Given: 5개의 시도 기록 (3개 정답, 2개 오답)
    now = datetime.utcnow()
    attempts_data = [True, True, False, True, False]
    for i, is_correct in enumerate(attempts_data):
        attempt = StudentAttempt(
            student_id="student_123",
            question_id=f"q_{i}",
            concept="이차방정식",
            is_correct=is_correct,
            attempted_at=now + timedelta(seconds=i)
        )
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mastery = await service.calculate_concept_mastery("student_123", "이차방정식")

    # Then: 숙련도는 0과 1 사이
    assert 0.0 <= mastery <= 1.0
    # 3개 정답, 2개 오답이므로 초기값(0.1)보다는 높아야 함
    assert mastery > 0.1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_multiple_concepts_mastery(db_session):
    """
    Test: 여러 개념에 대한 숙련도 계산
    Expected: {개념: 숙련도} 딕셔너리 반환
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    # Given: 3개 개념에 대한 시도 기록
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="이차방정식", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="이차방정식", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="삼각함수", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_4", concept="미분", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mastery_map = await service.calculate_multiple_concepts_mastery(
        "student_1",
        ["이차방정식", "삼각함수", "미분"]
    )

    # Then
    assert len(mastery_map) == 3
    assert "이차방정식" in mastery_map
    assert "삼각함수" in mastery_map
    assert "미분" in mastery_map
    # 이차방정식: 2개 정답 → 높은 숙련도
    assert mastery_map["이차방정식"] > 0.5
    # 삼각함수: 1개 오답 → 낮은 숙련도
    assert mastery_map["삼각함수"] < 0.5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_student_mastery_profile(db_session):
    """
    Test: 학생의 전체 숙련도 프로파일 조회
    Expected: 모든 학습한 개념의 숙련도 맵 반환
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    # Given: 여러 개념에 대한 시도 기록
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="B", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_4", concept="C", is_correct=True),
        # 다른 학생의 기록 (포함되지 않아야 함)
        StudentAttempt(student_id="student_2", question_id="q_5", concept="A", is_correct=False),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    profile = await service.get_student_mastery_profile("student_1")

    # Then
    assert len(profile) == 3  # A, B, C
    assert "A" in profile
    assert "B" in profile
    assert "C" in profile
    assert all(0.0 <= score <= 1.0 for score in profile.values())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_identify_weak_concepts(db_session):
    """
    Test: 약한 개념 식별
    Expected: 숙련도가 임계값 이하인 개념 리스트 반환
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    # Given: 다양한 숙련도의 개념들
    attempts = [
        # 개념 A: 모두 정답 (높은 숙련도)
        StudentAttempt(student_id="student_1", question_id="q_1", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="A", is_correct=True),
        # 개념 B: 모두 오답 (낮은 숙련도)
        StudentAttempt(student_id="student_1", question_id="q_4", concept="B", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_5", concept="B", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_6", concept="B", is_correct=False),
        # 개념 C: 혼합 (중간 숙련도)
        StudentAttempt(student_id="student_1", question_id="q_7", concept="C", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_8", concept="C", is_correct=False),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When: 임계값 0.5로 약한 개념 식별
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    weak_concepts = await service.identify_weak_concepts("student_1", threshold=0.5)

    # Then: B는 확실히 포함되어야 함
    assert "B" in weak_concepts
    # A는 포함되지 않아야 함
    assert "A" not in weak_concepts


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_concept_accuracy(db_session):
    """
    Test: 개념별 정답률 조회
    Expected: 정답률 반환
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    # Given: 10개 중 7개 정답
    for i in range(10):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="이차방정식",
            is_correct=(i < 7)
        )
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    accuracy = await service.get_concept_accuracy("student_1", "이차방정식")

    # Then
    assert accuracy == pytest.approx(0.7, abs=0.01)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mastery_service_with_custom_bkt_params(db_session):
    """
    Test: 커스텀 BKT 파라미터로 서비스 사용
    Expected: 커스텀 파라미터가 적용된 숙련도 계산
    """
    from app.services.mastery_service import MasteryService
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    # Given
    attempt = StudentAttempt(
        student_id="student_1",
        question_id="q_1",
        concept="개념1",
        is_correct=True
    )
    db_session.add(attempt)
    await db_session.commit()

    # When: 높은 p_learn 파라미터 사용
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing(p_init=0.2, p_learn=0.5)
    service = MasteryService(repo, bkt)
    mastery = await service.calculate_concept_mastery("student_1", "개념1")

    # Then: 높은 p_learn으로 인해 더 큰 숙련도 증가
    assert mastery > 0.5
