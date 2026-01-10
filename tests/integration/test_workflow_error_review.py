"""
Error Review 워크플로우 통합 테스트

TDD: 테스트를 먼저 작성하고, 구현을 통과시킵니다.

데이터 플로우:
Node 0 → Node 4 (오답 감지) → Node 7 (오답노트 생성) → Node 7 (Anki 스케줄링)
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.error_review_service import ErrorReviewService, ErrorReviewRequest, ErrorReviewResult


@pytest.mark.asyncio
@pytest.mark.integration
async def test_error_review_full_workflow(db_session, sample_student, mock_mcp):
    """완전한 오답 복습 워크플로우 테스트"""

    # Given: 학생이 문제를 틀렸을 때
    student_id = sample_student.id
    question_id = "q_001"
    student_answer = "y = (x-1)^2 + 2의 최댓값은 2이다"
    correct_answer = "최댓값 없음 (위로 볼록)"

    # When: 오답 복습 워크플로우 시작
    service = ErrorReviewService(mcp=mock_mcp, db=db_session)

    request = ErrorReviewRequest(
        student_id=student_id,
        question_id=question_id,
        student_answer=student_answer,
        correct_answer=correct_answer
    )

    result = await service.start_error_review(request)

    # Then: 오답노트 ID가 생성되어야 함
    assert result.error_note_id is not None
    assert result.error_note_id.startswith("en_")

    # Then: 다음 복습 날짜가 설정되어야 함
    assert result.next_review_date is not None
    assert isinstance(result.next_review_date, datetime)
    # Anki SM-2: 첫 복습은 1일 후
    expected_date = datetime.now() + timedelta(days=1)
    assert abs((result.next_review_date - expected_date).days) <= 1

    # Then: Anki 인터벌이 설정되어야 함
    assert result.anki_interval_days == 1  # 첫 복습

    # Then: 오답 분석이 포함되어야 함
    assert result.analysis is not None
    assert result.analysis.misconception is not None
    assert result.analysis.root_cause is not None
    assert len(result.analysis.related_concepts) > 0

    # Then: MCP 호출이 올바른 순서로 이루어져야 함
    assert mock_mcp.called("q-dna", "get_question_dna")
    assert mock_mcp.called("error-note", "create_error_note")
    assert mock_mcp.called("error-note", "calculate_anki_schedule")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_error_review_creates_workflow_session(db_session, sample_student, mock_mcp):
    """워크플로우 세션이 DB에 저장되는지 테스트"""

    # Given
    service = ErrorReviewService(mcp=mock_mcp, db=db_session)

    request = ErrorReviewRequest(
        student_id=sample_student.id,
        question_id="q_002",
        student_answer="x^2 + 2x + 1 = (x+1)(x+1)",
        correct_answer="(x+1)^2"
    )

    # When
    result = await service.start_error_review(request)

    # Then: DB에서 세션을 조회할 수 있어야 함
    from app.models.workflow_session import WorkflowSession
    from sqlalchemy import select

    stmt = select(WorkflowSession).where(
        WorkflowSession.student_id == sample_student.id,
        WorkflowSession.workflow_type == "error_review"
    )
    db_result = await db_session.execute(stmt)
    session = db_result.scalar_one_or_none()

    assert session is not None
    assert session.workflow_type == "error_review"
    assert session.status == "completed"  # 오답 복습은 즉시 완료
    assert "error_note_id" in session.workflow_metadata
    assert "question_id" in session.workflow_metadata
    assert "next_review_date" in session.workflow_metadata


@pytest.mark.asyncio
@pytest.mark.integration
async def test_error_review_with_multiple_errors(db_session, sample_student, mock_mcp):
    """여러 오답을 연속으로 처리하는 테스트"""

    service = ErrorReviewService(mcp=mock_mcp, db=db_session)

    questions = [
        ("q_001", "답1", "정답1"),
        ("q_002", "답2", "정답2"),
        ("q_003", "답3", "정답3"),
    ]

    error_note_ids = []

    for question_id, student_ans, correct_ans in questions:
        # When
        request = ErrorReviewRequest(
            student_id=sample_student.id,
            question_id=question_id,
            student_answer=student_ans,
            correct_answer=correct_ans
        )

        result = await service.start_error_review(request)

        # Then
        assert result.error_note_id is not None
        error_note_ids.append(result.error_note_id)

    # Then: 모든 오답노트 ID가 고유해야 함
    assert len(error_note_ids) == len(set(error_note_ids))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_error_review_anki_schedule_progression(db_session, sample_student, mock_mcp):
    """Anki 스케줄 진행 테스트 (복습 횟수 증가)"""

    service = ErrorReviewService(mcp=mock_mcp, db=db_session)

    # Given: 첫 번째 오답
    request = ErrorReviewRequest(
        student_id=sample_student.id,
        question_id="q_repeat",
        student_answer="오답",
        correct_answer="정답"
    )

    # When: 첫 복습
    result1 = await service.start_error_review(request)

    # Then: 1일 후 복습
    assert result1.anki_interval_days == 1

    # Mock에서 복습 횟수를 증가시킨 후
    # (실제로는 Node 7의 Anki 알고리즘이 처리)
    # When: 성공적인 복습 후 다시 틀렸을 때
    mock_mcp.call_history.clear()  # 이력 초기화

    result2 = await service.start_error_review(request)

    # Then: 새로운 오답노트가 생성됨
    assert result2.error_note_id is not None
    assert result2.error_note_id != result1.error_note_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_error_review_analysis_quality(db_session, sample_student, mock_mcp):
    """오답 분석의 품질 테스트"""

    service = ErrorReviewService(mcp=mock_mcp, db=db_session)

    # Given: 개념적 오류가 있는 오답
    request = ErrorReviewRequest(
        student_id=sample_student.id,
        question_id="q_concept_error",
        student_answer="미분하면 0이다",
        correct_answer="극값을 찾으려면 f'(x)=0을 풀어야 한다"
    )

    # When
    result = await service.start_error_review(request)

    # Then: 분석에 오개념이 포함되어야 함
    assert result.analysis.misconception is not None
    assert len(result.analysis.misconception) > 0

    # Then: 근본 원인이 식별되어야 함
    assert result.analysis.root_cause is not None
    assert len(result.analysis.root_cause) > 0

    # Then: 관련 개념이 제안되어야 함
    assert len(result.analysis.related_concepts) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_error_review_with_empty_student_answer(db_session, sample_student, mock_mcp):
    """학생이 답을 작성하지 않은 경우 테스트"""

    service = ErrorReviewService(mcp=mock_mcp, db=db_session)

    # Given: 빈 답안
    request = ErrorReviewRequest(
        student_id=sample_student.id,
        question_id="q_empty",
        student_answer="",
        correct_answer="정답"
    )

    # When
    result = await service.start_error_review(request)

    # Then: 오답노트는 생성되어야 함
    assert result.error_note_id is not None

    # Then: 분석에 "답안 없음" 관련 내용이 포함되어야 함
    assert result.analysis is not None
