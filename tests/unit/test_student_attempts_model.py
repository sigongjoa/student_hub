"""
Unit Tests for StudentAttempt Model

TDD: Red-Green-Refactor
- Write failing tests first
- Implement minimal code to pass
- Refactor while keeping tests green

Target: 100% code coverage
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_student_attempt_success(db_session):
    """
    Test: Create student attempt with all required fields
    Expected: Attempt created successfully with auto-generated ID and timestamp
    """
    from app.models.student_attempt import StudentAttempt

    attempt = StudentAttempt(
        student_id="student_123",
        question_id="q_456",
        concept="도함수",
        is_correct=True,
        response_time_ms=45000
    )

    db_session.add(attempt)
    await db_session.commit()
    await db_session.refresh(attempt)

    assert attempt.id is not None
    assert attempt.student_id == "student_123"
    assert attempt.question_id == "q_456"
    assert attempt.concept == "도함수"
    assert attempt.is_correct is True
    assert attempt.response_time_ms == 45000
    assert attempt.attempted_at is not None
    assert isinstance(attempt.attempted_at, datetime)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_student_attempt_missing_required_field(db_session):
    """
    Test: Create attempt without required field (student_id)
    Expected: Raises IntegrityError
    """
    from app.models.student_attempt import StudentAttempt

    attempt = StudentAttempt(
        # student_id missing!
        question_id="q_456",
        concept="도함수",
        is_correct=True
    )

    db_session.add(attempt)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_student_attempt_default_timestamp(db_session):
    """
    Test: Attempt timestamp defaults to now()
    Expected: attempted_at is set automatically
    """
    from app.models.student_attempt import StudentAttempt

    before = datetime.utcnow()
    attempt = StudentAttempt(
        student_id="student_123",
        question_id="q_456",
        concept="도함수",
        is_correct=True
    )

    db_session.add(attempt)
    await db_session.commit()
    await db_session.refresh(attempt)

    after = datetime.utcnow()

    assert before <= attempt.attempted_at <= after


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_attempts_by_student(db_session):
    """
    Test: Query all attempts for a specific student
    Expected: Returns only that student's attempts
    """
    from app.models.student_attempt import StudentAttempt

    # Create attempts for different students
    attempt1 = StudentAttempt(
        student_id="student_123",
        question_id="q_1",
        concept="도함수",
        is_correct=True
    )
    attempt2 = StudentAttempt(
        student_id="student_123",
        question_id="q_2",
        concept="적분",
        is_correct=False
    )
    attempt3 = StudentAttempt(
        student_id="student_456",
        question_id="q_3",
        concept="도함수",
        is_correct=True
    )

    db_session.add_all([attempt1, attempt2, attempt3])
    await db_session.commit()

    # Query attempts for student_123
    stmt = select(StudentAttempt).where(
        StudentAttempt.student_id == "student_123"
    )
    result = await db_session.execute(stmt)
    attempts = result.scalars().all()

    assert len(attempts) == 2
    assert all(a.student_id == "student_123" for a in attempts)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_attempts_by_concept(db_session):
    """
    Test: Query all attempts for a specific concept
    Expected: Returns only that concept's attempts
    """
    from app.models.student_attempt import StudentAttempt

    # Create attempts for different concepts
    attempt1 = StudentAttempt(
        student_id="student_123",
        question_id="q_1",
        concept="도함수",
        is_correct=True
    )
    attempt2 = StudentAttempt(
        student_id="student_123",
        question_id="q_2",
        concept="도함수",
        is_correct=False
    )
    attempt3 = StudentAttempt(
        student_id="student_123",
        question_id="q_3",
        concept="적분",
        is_correct=True
    )

    db_session.add_all([attempt1, attempt2, attempt3])
    await db_session.commit()

    # Query attempts for "도함수"
    stmt = select(StudentAttempt).where(
        StudentAttempt.concept == "도함수"
    )
    result = await db_session.execute(stmt)
    attempts = result.scalars().all()

    assert len(attempts) == 2
    assert all(a.concept == "도함수" for a in attempts)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_concept_accuracy(db_session):
    """
    Test: Calculate accuracy for a concept
    Expected: Correct accuracy percentage
    """
    from app.models.student_attempt import StudentAttempt

    # Create mixed correctness attempts
    attempts_data = [
        {"student_id": "student_123", "question_id": f"q_{i}",
         "concept": "도함수", "is_correct": i % 2 == 0}
        for i in range(10)
    ]

    for data in attempts_data:
        db_session.add(StudentAttempt(**data))

    await db_session.commit()

    # Query and calculate accuracy
    stmt = select(StudentAttempt).where(
        StudentAttempt.student_id == "student_123",
        StudentAttempt.concept == "도함수"
    )
    result = await db_session.execute(stmt)
    attempts = result.scalars().all()

    correct_count = sum(1 for a in attempts if a.is_correct)
    accuracy = correct_count / len(attempts)

    assert len(attempts) == 10
    assert accuracy == 0.5  # 50% correct (0, 2, 4, 6, 8)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_recent_attempts(db_session):
    """
    Test: Query attempts from last 7 days
    Expected: Returns only recent attempts
    """
    from app.models.student_attempt import StudentAttempt

    now = datetime.utcnow()

    # Create old and recent attempts
    old_attempt = StudentAttempt(
        student_id="student_123",
        question_id="q_old",
        concept="도함수",
        is_correct=True,
        attempted_at=now - timedelta(days=10)
    )

    recent_attempt = StudentAttempt(
        student_id="student_123",
        question_id="q_recent",
        concept="도함수",
        is_correct=True,
        attempted_at=now - timedelta(days=3)
    )

    db_session.add_all([old_attempt, recent_attempt])
    await db_session.commit()

    # Query recent attempts (last 7 days)
    cutoff_date = now - timedelta(days=7)
    stmt = select(StudentAttempt).where(
        StudentAttempt.student_id == "student_123",
        StudentAttempt.attempted_at >= cutoff_date
    )
    result = await db_session.execute(stmt)
    recent_attempts = result.scalars().all()

    assert len(recent_attempts) == 1
    assert recent_attempts[0].question_id == "q_recent"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_student_attempt_repr(db_session):
    """
    Test: String representation of StudentAttempt
    Expected: Readable string with key information
    """
    from app.models.student_attempt import StudentAttempt

    attempt = StudentAttempt(
        student_id="student_123",
        question_id="q_456",
        concept="도함수",
        is_correct=True
    )

    db_session.add(attempt)
    await db_session.commit()
    await db_session.refresh(attempt)

    repr_str = repr(attempt)
    assert "StudentAttempt" in repr_str
    assert "student_123" in repr_str
    assert "q_456" in repr_str
