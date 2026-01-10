"""
Learning Path 워크플로우 통합 테스트

TDD: 테스트를 먼저 작성하고, 구현을 통과시킵니다.

데이터 플로우:
Node 0 → Node 4 (히트맵) → Node 1 (선수지식 그래프) → Node 2 (학습 경로 생성)
"""
import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.learning_path_service import LearningPathService, LearningPathRequest, LearningPathResult


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_full_workflow(db_session, sample_student, mock_mcp):
    """완전한 학습 경로 생성 워크플로우 테스트"""

    # Given: 학생이 목표 개념을 설정했을 때
    student_id = sample_student.id
    target_concept = "적분"
    days = 14  # 2주

    # When: 학습 경로 생성 요청
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=student_id,
        target_concept=target_concept,
        days=days
    )

    result = await service.generate_learning_path(request)

    # Then: 워크플로우 ID가 생성되어야 함
    assert result.workflow_id is not None
    assert result.workflow_id.startswith("wf_")

    # Then: 학습 경로가 생성되어야 함
    assert result.learning_path is not None
    assert len(result.learning_path) > 0

    # Then: 선수지식 순서가 올바라야 함 (Topological Sort)
    # 극한 → 도함수 → 적분 순서
    concept_names = [node.concept for node in result.learning_path]
    assert concept_names.index("극한") < concept_names.index("도함수")
    assert concept_names.index("도함수") < concept_names.index("적분")

    # Then: 각 노드가 order를 가져야 함
    for i, node in enumerate(result.learning_path):
        assert node.order == i + 1

    # Then: 총 예상 시간이 계산되어야 함
    assert result.total_estimated_hours > 0
    assert result.total_estimated_hours == sum(node.estimated_hours for node in result.learning_path)

    # Then: 일일 태스크가 할당되어야 함
    assert result.daily_tasks is not None
    assert len(result.daily_tasks) > 0

    # Then: MCP 호출이 올바른 순서로 이루어져야 함
    assert mock_mcp.called("lab-node", "get_concept_heatmap")
    assert mock_mcp.called("logic-engine", "get_prerequisite_graph")
    assert mock_mcp.called("q-dna", "estimate_learning_time")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_creates_workflow_session(db_session, sample_student, mock_mcp):
    """워크플로우 세션이 DB에 저장되는지 테스트"""

    # Given
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="미분",
        days=7
    )

    # When
    result = await service.generate_learning_path(request)

    # Then: DB에서 세션을 조회할 수 있어야 함
    from app.models.workflow_session import WorkflowSession
    from sqlalchemy import select

    stmt = select(WorkflowSession).where(
        WorkflowSession.student_id == sample_student.id,
        WorkflowSession.workflow_type == "learning_path"
    )
    db_result = await db_session.execute(stmt)
    session = db_result.scalar_one_or_none()

    assert session is not None
    assert session.workflow_type == "learning_path"
    assert session.status == "in_progress"
    assert "target_concept" in session.workflow_metadata
    assert "learning_path" in session.workflow_metadata
    assert "total_estimated_hours" in session.workflow_metadata


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_topological_sort(db_session, sample_student, mock_mcp):
    """Topological Sort가 선수지식 순서를 올바르게 정렬하는지 테스트"""

    # Given
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="적분",
        days=21
    )

    # When
    result = await service.generate_learning_path(request)

    # Then: 각 개념의 선수지식이 먼저 나와야 함
    concept_positions = {node.concept: i for i, node in enumerate(result.learning_path)}

    for node in result.learning_path:
        for prereq in node.prerequisites:
            if prereq in concept_positions:
                assert concept_positions[prereq] < concept_positions[node.concept], \
                    f"{prereq}는 {node.concept}보다 먼저 와야 합니다"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_with_weak_concepts_prioritization(db_session, sample_student, mock_mcp):
    """약점 개념이 우선적으로 포함되는지 테스트"""

    # Given: 학생이 특정 개념에 약함 (히트맵에서 < 0.6)
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="적분",
        days=14
    )

    # When
    result = await service.generate_learning_path(request)

    # Then: 약점 개념이 경로에 포함되어야 함
    concept_names = [node.concept for node in result.learning_path]
    # Mock에서 극한=0.45, 도함수=0.55로 설정 (< 0.6)
    assert "극한" in concept_names
    assert "도함수" in concept_names


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_daily_task_allocation(db_session, sample_student, mock_mcp):
    """일일 태스크가 합리적으로 분배되는지 테스트"""

    # Given
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="적분",
        days=14
    )

    # When
    result = await service.generate_learning_path(request)

    # Then: 일일 태스크 총합이 전체 기간과 일치해야 함
    total_hours_allocated = sum(result.daily_tasks.values())
    assert total_hours_allocated == result.total_estimated_hours

    # Then: 하루에 너무 많은 시간이 할당되지 않아야 함 (< 5시간)
    for day, hours in result.daily_tasks.items():
        assert hours <= 5, f"{day}에 {hours}시간은 너무 많습니다"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_with_short_duration(db_session, sample_student, mock_mcp):
    """짧은 기간(7일)에도 경로가 생성되는지 테스트"""

    # Given
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="도함수",
        days=7
    )

    # When
    result = await service.generate_learning_path(request)

    # Then: 경로가 생성되어야 함
    assert result.learning_path is not None
    assert len(result.learning_path) > 0

    # Then: 일일 학습량이 조정되어야 함
    # 7일에 맞춰서 하루 학습량이 늘어날 수 있음
    assert len(result.daily_tasks) <= 7


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_with_multiple_targets(db_session, sample_student, mock_mcp):
    """여러 목표 개념이 있을 때 테스트"""

    # Given
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    # When: 목표 개념을 여러 개 설정 (쉼표로 구분)
    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="도함수,적분",  # 두 개념
        days=21
    )

    result = await service.generate_learning_path(request)

    # Then: 두 목표 개념이 모두 경로에 포함되어야 함
    concept_names = [node.concept for node in result.learning_path]
    assert "도함수" in concept_names
    assert "적분" in concept_names


@pytest.mark.asyncio
@pytest.mark.integration
async def test_learning_path_estimated_time_calculation(db_session, sample_student, mock_mcp):
    """학습 시간 추정이 BKT 숙련도를 반영하는지 테스트"""

    # Given
    service = LearningPathService(mcp=mock_mcp, db=db_session)

    request = LearningPathRequest(
        student_id=sample_student.id,
        target_concept="적분",
        days=14
    )

    # When
    result = await service.generate_learning_path(request)

    # Then: 각 노드가 예상 시간을 가져야 함
    for node in result.learning_path:
        assert node.estimated_hours > 0
        # 한 개념당 20시간을 넘지 않아야 함 (현실적인 범위)
        assert node.estimated_hours <= 20

    # Then: Node 2의 estimate_learning_time이 호출되었어야 함
    assert mock_mcp.called("q-dna", "estimate_learning_time")
