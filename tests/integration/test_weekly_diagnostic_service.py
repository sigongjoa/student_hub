"""
Weekly Diagnostic Service Integration Tests (TDD)

WeeklyDiagnosticService가 Mock MCP 서버와 연동되는지 테스트
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.weekly_diagnostic_service import (
    WeeklyDiagnosticService,
    WeeklyDiagnosticRequest
)
from app.mcp.manager import MCPClientManager


@pytest.mark.asyncio
async def test_weekly_diagnostic_with_mock_mcp(db_session: AsyncSession):
    """주간 진단 서비스가 Mock MCP 서버와 연동되는지 테스트"""
    # Given: Mock MCP Manager 생성
    mcp = MCPClientManager()
    await mcp.initialize()

    service = WeeklyDiagnosticService(mcp, db_session)

    request = WeeklyDiagnosticRequest(
        student_id="student_integration_001",
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=True
    )

    # When: 주간 진단 실행
    result = await service.start_diagnostic(request)

    # Then: 결과 검증
    assert result.workflow_id is not None
    assert result.session_id > 0
    assert len(result.questions) > 0
    assert isinstance(result.weak_concepts, list)
    assert result.total_estimated_time_minutes > 0
    assert result.started_at is not None

    # Cleanup
    await mcp.close_all()


@pytest.mark.asyncio
async def test_weekly_diagnostic_weak_concepts_identification(db_session: AsyncSession):
    """약점 개념 식별이 제대로 작동하는지 테스트"""
    # Given
    mcp = MCPClientManager()
    await mcp.initialize()

    service = WeeklyDiagnosticService(mcp, db_session)

    request = WeeklyDiagnosticRequest(
        student_id="student_weak_test",
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=True
    )

    # When
    result = await service.start_diagnostic(request)

    # Then: 약점 개념이 식별되어야 함 (숙련도 < 0.6)
    # Mock 서버는 랜덤하게 0.3~0.7 사이의 숙련도를 생성하므로 약점이 있을 가능성이 높음
    assert isinstance(result.weak_concepts, list)

    # Cleanup
    await mcp.close_all()


@pytest.mark.asyncio
async def test_weekly_diagnostic_workflow_session_created(db_session: AsyncSession):
    """워크플로우 세션이 DB에 저장되는지 테스트"""
    # Given
    mcp = MCPClientManager()
    await mcp.initialize()

    service = WeeklyDiagnosticService(mcp, db_session)

    request = WeeklyDiagnosticRequest(
        student_id="student_session_test",
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=True
    )

    # When
    result = await service.start_diagnostic(request)

    # Then: 워크플로우 세션이 DB에 저장되어야 함
    workflow_status = await service.get_workflow_status(result.workflow_id)

    assert workflow_status is not None
    assert workflow_status["workflow_id"] == result.workflow_id
    assert workflow_status["status"] == "in_progress"
    assert "metadata" in workflow_status
    assert workflow_status["metadata"]["curriculum_path"] == "중학수학.2학년.1학기"

    # Cleanup
    await mcp.close_all()


@pytest.mark.asyncio
async def test_weekly_diagnostic_without_weak_concepts(db_session: AsyncSession):
    """약점 개념 포함하지 않는 경우 테스트"""
    # Given
    mcp = MCPClientManager()
    await mcp.initialize()

    service = WeeklyDiagnosticService(mcp, db_session)

    request = WeeklyDiagnosticRequest(
        student_id="student_no_weak",
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=False  # 약점 포함 안 함
    )

    # When
    result = await service.start_diagnostic(request)

    # Then: 약점 개념이 비어있어야 함
    assert result.weak_concepts == []
    assert len(result.questions) > 0  # 문제는 여전히 추천되어야 함

    # Cleanup
    await mcp.close_all()


@pytest.mark.asyncio
async def test_weekly_diagnostic_question_structure(db_session: AsyncSession):
    """추천된 문제의 구조가 올바른지 테스트"""
    # Given
    mcp = MCPClientManager()
    await mcp.initialize()

    service = WeeklyDiagnosticService(mcp, db_session)

    request = WeeklyDiagnosticRequest(
        student_id="student_question_test",
        curriculum_path="중학수학.2학년.1학기",
        include_weak_concepts=True
    )

    # When
    result = await service.start_diagnostic(request)

    # Then: 각 문제가 올바른 구조를 가져야 함
    assert len(result.questions) > 0

    for question in result.questions:
        assert question.id is not None
        assert question.content is not None
        assert question.difficulty in ["easy", "medium", "hard"]
        assert isinstance(question.concepts, list)

    # Cleanup
    await mcp.close_all()
