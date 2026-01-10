"""
Weekly Diagnostic 워크플로우 통합 테스트

TDD: 테스트를 먼저 작성하고, 구현을 통과시킵니다.
"""
import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.weekly_diagnostic_service import WeeklyDiagnosticService, WeeklyDiagnosticRequest, WeeklyDiagnosticResult


@pytest.mark.asyncio
@pytest.mark.integration
async def test_weekly_diagnostic_full_workflow(db_session, sample_student, mock_mcp):
    """완전한 주간 진단 워크플로우 테스트"""

    # Given: 학습 이력이 있는 학생
    student_id = sample_student.id
    curriculum_path = "중학수학.2학년.1학기"

    # When: 주간 진단 요청
    service = WeeklyDiagnosticService(mcp=mock_mcp, db=db_session)

    request = WeeklyDiagnosticRequest(
        student_id=student_id,
        curriculum_path=curriculum_path,
        include_weak_concepts=True
    )

    result = await service.start_diagnostic(request)

    # Then: 워크플로우 ID와 세션 ID가 생성되어야 함
    assert result.workflow_id is not None
    assert result.workflow_id.startswith("wf_")
    assert result.session_id is not None

    # Then: 문제가 추천되어야 함
    assert result.questions is not None
    assert len(result.questions) == 10  # 기본 10문제

    # Then: 약점 개념이 식별되어야 함
    assert result.weak_concepts is not None
    assert len(result.weak_concepts) > 0
    assert "도함수" in result.weak_concepts  # Mock에서 0.45로 설정

    # Then: 예상 시간이 계산되어야 함
    assert result.total_estimated_time_minutes > 0

    # Then: 시작 시간이 기록되어야 함
    assert result.started_at is not None
    assert isinstance(result.started_at, datetime)

    # Then: MCP 호출이 올바른 순서로 이루어져야 함
    assert mock_mcp.called("q-dna", "get_student_mastery")
    assert mock_mcp.called("q-dna", "recommend_questions")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_weekly_diagnostic_without_weak_concepts(db_session, sample_student, mock_mcp):
    """약점 개념 제외 옵션 테스트"""

    # Given
    service = WeeklyDiagnosticService(mcp=mock_mcp, db=db_session)

    request = WeeklyDiagnosticRequest(
        student_id=sample_student.id,
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=False
    )

    # When
    result = await service.start_diagnostic(request)

    # Then: 문제는 추천되지만 약점 분석은 스킵
    assert result.questions is not None
    assert len(result.questions) == 10


@pytest.mark.asyncio
@pytest.mark.integration
async def test_weekly_diagnostic_saves_workflow_session(db_session, sample_student, mock_mcp):
    """워크플로우 세션이 DB에 저장되는지 테스트"""

    # Given
    service = WeeklyDiagnosticService(mcp=mock_mcp, db=db_session)

    request = WeeklyDiagnosticRequest(
        student_id=sample_student.id,
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=True
    )

    # When
    result = await service.start_diagnostic(request)

    # Then: DB에서 세션을 조회할 수 있어야 함
    from app.models.workflow_session import WorkflowSession
    from sqlalchemy import select

    stmt = select(WorkflowSession).where(WorkflowSession.workflow_id == result.workflow_id)
    db_result = await db_session.execute(stmt)
    session = db_result.scalar_one_or_none()

    assert session is not None
    assert session.student_id == sample_student.id
    assert session.workflow_type == "weekly_diagnostic"
    assert session.status == "in_progress"
    assert "questions" in session.workflow_metadata
    assert "weak_concepts" in session.workflow_metadata


@pytest.mark.asyncio
@pytest.mark.integration
async def test_weekly_diagnostic_with_different_curriculum_paths(db_session, sample_student, mock_mcp):
    """다양한 교육과정 경로 테스트"""

    service = WeeklyDiagnosticService(mcp=mock_mcp, db=db_session)

    test_paths = [
        "고등수학.미적분.도함수",
        "중학수학.1학년.정수와유리수",
        "초등수학.6학년.분수의나눗셈"
    ]

    for path in test_paths:
        # When
        request = WeeklyDiagnosticRequest(
            student_id=sample_student.id,
            curriculum_path=path,
            include_weak_concepts=True
        )

        result = await service.start_diagnostic(request)

        # Then
        assert result.workflow_id is not None
        assert result.questions is not None
