"""
Unit Tests for StudentAttemptRepository

TDD: Repository 패턴의 데이터 접근 로직 검증

Repository Pattern:
- 데이터 접근 로직을 캡슐화
- 비즈니스 로직과 데이터 계층 분리
- 테스트 가능한 인터페이스 제공

Target: 100% code coverage
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_attempt(db_session):
    """
    Test: 시도 기록 생성
    Expected: 정상적으로 생성되고 ID가 할당됨
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository

    repo = StudentAttemptRepository(db_session)

    attempt = await repo.create_attempt(
        student_id="student_123",
        question_id="q_456",
        concept="이차방정식",
        is_correct=True,
        response_time_ms=45000
    )

    assert attempt.id is not None
    assert attempt.student_id == "student_123"
    assert attempt.question_id == "q_456"
    assert attempt.concept == "이차방정식"
    assert attempt.is_correct is True
    assert attempt.response_time_ms == 45000
    assert attempt.attempted_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id(db_session):
    """
    Test: ID로 시도 기록 조회
    Expected: 해당 ID의 시도 기록 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 시도 기록 생성
    attempt = StudentAttempt(
        student_id="student_123",
        question_id="q_456",
        concept="이차방정식",
        is_correct=True,
        response_time_ms=45000
    )
    db_session.add(attempt)
    await db_session.commit()
    await db_session.refresh(attempt)

    # When: ID로 조회
    repo = StudentAttemptRepository(db_session)
    found = await repo.get_by_id(attempt.id)

    # Then
    assert found is not None
    assert found.id == attempt.id
    assert found.student_id == "student_123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    """
    Test: 존재하지 않는 ID 조회
    Expected: None 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository

    repo = StudentAttemptRepository(db_session)
    found = await repo.get_by_id(99999)

    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_student(db_session):
    """
    Test: 학생 ID로 시도 기록 조회
    Expected: 해당 학생의 모든 시도 기록 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 여러 학생의 시도 기록
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="개념1", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="개념2", is_correct=False),
        StudentAttempt(student_id="student_2", question_id="q_3", concept="개념1", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When: student_1의 시도 기록 조회
    repo = StudentAttemptRepository(db_session)
    results = await repo.get_by_student("student_1")

    # Then
    assert len(results) == 2
    assert all(a.student_id == "student_1" for a in results)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_student_with_pagination(db_session):
    """
    Test: 페이지네이션으로 학생 시도 기록 조회
    Expected: limit, offset에 따라 결과 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 10개의 시도 기록
    for i in range(10):
        attempt = StudentAttempt(
            student_id="student_123",
            question_id=f"q_{i}",
            concept="개념1",
            is_correct=True
        )
        db_session.add(attempt)
    await db_session.commit()

    # When: limit=5, offset=2
    repo = StudentAttemptRepository(db_session)
    results = await repo.get_by_student("student_123", limit=5, offset=2)

    # Then
    assert len(results) == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_concept(db_session):
    """
    Test: 학생 ID와 개념으로 시도 기록 조회
    Expected: 해당 학생의 특정 개념 시도 기록만 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="이차방정식", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="이차방정식", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="삼각함수", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    results = await repo.get_by_concept("student_1", "이차방정식")

    # Then
    assert len(results) == 2
    assert all(a.concept == "이차방정식" for a in results)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_recent_attempts(db_session):
    """
    Test: 최근 N일 이내 시도 기록 조회
    Expected: 지정된 기간 내 시도 기록만 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 다양한 시간의 시도 기록
    now = datetime.utcnow()
    attempts = [
        StudentAttempt(
            student_id="student_1",
            question_id="q_1",
            concept="개념1",
            is_correct=True,
            attempted_at=now - timedelta(days=1)  # 1일 전
        ),
        StudentAttempt(
            student_id="student_1",
            question_id="q_2",
            concept="개념1",
            is_correct=True,
            attempted_at=now - timedelta(days=5)  # 5일 전
        ),
        StudentAttempt(
            student_id="student_1",
            question_id="q_3",
            concept="개념1",
            is_correct=True,
            attempted_at=now - timedelta(days=10)  # 10일 전
        ),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When: 최근 7일 이내 시도 기록 조회
    repo = StudentAttemptRepository(db_session)
    results = await repo.get_recent_attempts("student_1", days=7)

    # Then: 1일 전, 5일 전 기록만 반환
    assert len(results) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_recent_attempts_with_limit(db_session):
    """
    Test: 최근 시도 기록 조회 with limit
    Expected: 최대 limit개 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 5개의 최근 시도 기록
    now = datetime.utcnow()
    for i in range(5):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="개념1",
            is_correct=True,
            attempted_at=now - timedelta(hours=i)
        )
        db_session.add(attempt)
    await db_session.commit()

    # When: limit=3
    repo = StudentAttemptRepository(db_session)
    results = await repo.get_recent_attempts("student_1", days=1, limit=3)

    # Then
    assert len(results) == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_concept_accuracy(db_session):
    """
    Test: 개념별 정답률 계산
    Expected: (정답 수 / 전체 시도 수) 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 10개 중 7개 정답
    for i in range(10):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="이차방정식",
            is_correct=(i < 7)  # 0~6번은 정답
        )
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    accuracy = await repo.calculate_concept_accuracy("student_1", "이차방정식")

    # Then
    assert accuracy == pytest.approx(0.7, abs=0.01)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_concept_accuracy_no_attempts(db_session):
    """
    Test: 시도 기록이 없을 때 정답률 계산
    Expected: 0.0 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository

    repo = StudentAttemptRepository(db_session)
    accuracy = await repo.calculate_concept_accuracy("student_1", "존재하지_않는_개념")

    assert accuracy == 0.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_student_mastery_data(db_session):
    """
    Test: BKT 계산을 위한 학생 숙련도 데이터 조회
    Expected: is_correct 값들의 리스트 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given: 시간순으로 명확한 타임스탬프를 가진 시도 기록
    now = datetime.utcnow()
    attempts_data = [True, True, False, True, False]
    for i, is_correct in enumerate(attempts_data):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="이차방정식",
            is_correct=is_correct,
            attempted_at=now + timedelta(seconds=i)  # 각각 1초씩 차이
        )
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    mastery_data = await repo.get_student_mastery_data("student_1", "이차방정식")

    # Then
    assert len(mastery_data) == 5
    assert all(isinstance(item, dict) for item in mastery_data)
    assert all("is_correct" in item for item in mastery_data)
    # 시간순(오래된 것부터)으로 정렬되어야 함
    assert [item["is_correct"] for item in mastery_data] == attempts_data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_attempts_by_student(db_session):
    """
    Test: 학생의 총 시도 횟수 조회
    Expected: 해당 학생의 시도 기록 개수 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    # Given
    for i in range(7):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="개념1",
            is_correct=True
        )
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    count = await repo.count_attempts_by_student("student_1")

    # Then
    assert count == 7


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_attempt(db_session):
    """
    Test: 시도 기록 삭제
    Expected: 정상적으로 삭제됨
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
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
    await db_session.refresh(attempt)
    attempt_id = attempt.id

    # When
    repo = StudentAttemptRepository(db_session)
    result = await repo.delete_attempt(attempt_id)

    # Then
    assert result is True
    found = await repo.get_by_id(attempt_id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_attempt_not_found(db_session):
    """
    Test: 존재하지 않는 시도 기록 삭제
    Expected: False 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository

    repo = StudentAttemptRepository(db_session)
    result = await repo.delete_attempt(99999)

    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_attempt_returns_persisted_object(db_session):
    """
    Test: create_attempt가 영속화된 객체를 반환하는지 확인
    Expected: ID가 할당된 StudentAttempt 객체 반환
    """
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.models.student_attempt import StudentAttempt

    repo = StudentAttemptRepository(db_session)

    # When
    returned_attempt = await repo.create_attempt(
        student_id="student_999",
        question_id="q_999",
        concept="테스트개념",
        is_correct=True,
        response_time_ms=12345
    )

    # Then: 반환된 객체 검증
    assert returned_attempt is not None
    assert isinstance(returned_attempt, StudentAttempt)
    assert returned_attempt.id is not None
    assert returned_attempt.student_id == "student_999"
    assert returned_attempt.question_id == "q_999"
    assert returned_attempt.concept == "테스트개념"
    assert returned_attempt.is_correct is True
    assert returned_attempt.response_time_ms == 12345

    # DB에서 다시 조회해서 확인
    found = await repo.get_by_id(returned_attempt.id)
    assert found is not None
    assert found.id == returned_attempt.id
