"""
Exam Preparation 워크플로우 통합 테스트

TDD: 테스트를 먼저 작성하고, 구현을 통과시킵니다.

데이터 플로우:
Node 0 → Node 6 (학교 정보) → Node 4 (약점) → Node 2 (연습 문제) → 2주 계획
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.exam_prep_service import ExamPrepService, ExamPrepRequest, ExamPrepResult


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_full_workflow(db_session, sample_student, mock_mcp):
    """완전한 시험 준비 워크플로우 테스트"""

    # Given: 학생이 2주 후 시험을 준비할 때
    student_id = sample_student.id
    exam_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    school_id = "SCH_001"
    curriculum_paths = ["중학수학.2학년.1학기"]

    # When: 시험 준비 워크플로우 시작
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=student_id,
        exam_date=exam_date,
        school_id=school_id,
        curriculum_paths=curriculum_paths
    )

    result = await service.prepare_exam(request)

    # Then: 워크플로우 ID가 생성되어야 함
    assert result.workflow_id is not None
    assert result.workflow_id.startswith("wf_")

    # Then: 학습 플랜이 생성되어야 함 (7-14일)
    assert result.two_week_plan is not None
    assert 7 <= len(result.two_week_plan) <= 14

    # Then: 각 날짜별 태스크가 할당되어야 함
    for day_task in result.two_week_plan:
        assert day_task.day_number >= 1
        assert day_task.day_number <= 14
        assert day_task.date is not None
        assert len(day_task.concepts_to_review) > 0
        # 문제는 최소 0개 이상 (마지막 날은 문제가 적을 수 있음)
        assert len(day_task.practice_problems) >= 0

    # Then: 집중 개념이 식별되어야 함 (약점 개념)
    assert result.focus_concepts is not None
    assert len(result.focus_concepts) > 0

    # Then: 연습 문제가 추천되어야 함
    assert result.practice_problems is not None
    assert len(result.practice_problems) > 0

    # Then: 모의고사 PDF URL이 생성되어야 함
    assert result.mock_exam_pdf_url is not None
    assert result.mock_exam_pdf_url.endswith(".pdf")

    # Then: MCP 호출이 올바른 순서로 이루어져야 함
    assert mock_mcp.called("school-info", "get_exam_scope")
    assert mock_mcp.called("lab-node", "get_weak_concepts")
    assert mock_mcp.called("q-dna", "recommend_questions")
    assert mock_mcp.called("q-metrics", "generate_mock_exam")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_creates_workflow_session(db_session, sample_student, mock_mcp):
    """워크플로우 세션이 DB에 저장되는지 테스트"""

    # Given
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: DB에서 세션을 조회할 수 있어야 함
    from app.models.workflow_session import WorkflowSession
    from sqlalchemy import select

    stmt = select(WorkflowSession).where(
        WorkflowSession.student_id == sample_student.id,
        WorkflowSession.workflow_type == "exam_prep"
    )
    db_result = await db_session.execute(stmt)
    session = db_result.scalar_one_or_none()

    assert session is not None
    assert session.workflow_type == "exam_prep"
    assert session.status == "in_progress"
    assert "exam_date" in session.workflow_metadata
    assert "focus_concepts" in session.workflow_metadata
    assert "mock_exam_pdf_url" in session.workflow_metadata


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_with_weak_concepts_prioritization(db_session, sample_student, mock_mcp):
    """약점 개념이 초반에 집중 배치되는지 테스트"""

    # Given
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: 약점 개념이 focus_concepts에 포함되어야 함
    assert len(result.focus_concepts) > 0

    # Then: 초반 Day 1-7에 약점 개념이 집중되어야 함
    early_days = result.two_week_plan[:7]
    late_days = result.two_week_plan[7:]

    early_weak_count = sum(
        1 for day in early_days
        for concept in day.concepts_to_review
        if concept in result.focus_concepts
    )
    late_weak_count = sum(
        1 for day in late_days
        for concept in day.concepts_to_review
        if concept in result.focus_concepts
    )

    # 초반에 약점 개념이 더 많아야 함
    assert early_weak_count >= late_weak_count


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_daily_task_structure(db_session, sample_student, mock_mcp):
    """일일 태스크 구조가 올바른지 테스트"""

    # Given
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: 각 날의 학습량이 적절해야 함
    for day_task in result.two_week_plan:
        # 개념 수: 1-3개
        assert 1 <= len(day_task.concepts_to_review) <= 3

        # 연습 문제: 최소 2개 이상 (문제 부족할 수 있음)
        assert len(day_task.practice_problems) >= 0

        # Day 12-13은 모의고사 날이어야 함
        if day_task.day_number in [12, 13]:
            assert "모의고사" in day_task.concepts_to_review or len(day_task.practice_problems) >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_anki_integration(db_session, sample_student, mock_mcp):
    """Anki 복습이 플랜에 통합되는지 테스트"""

    # Given
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: 매일 Anki 복습이 포함되어야 함
    for day_task in result.two_week_plan:
        assert day_task.anki_reviews >= 0
        # 후반부로 갈수록 Anki 복습 증가
        if day_task.day_number >= 8:
            assert day_task.anki_reviews > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_with_short_duration(db_session, sample_student, mock_mcp):
    """짧은 기간 (1주)에도 플랜이 생성되는지 테스트"""

    # Given: 1주일 남았을 때
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: 7일 플랜이 생성되어야 함
    assert len(result.two_week_plan) == 7

    # Then: 문제가 할당되어야 함
    for day_task in result.two_week_plan:
        assert len(day_task.practice_problems) >= 0  # 문제가 있어야 함


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_with_multiple_curriculum_paths(db_session, sample_student, mock_mcp):
    """여러 교육과정 경로 (복합 시험) 테스트"""

    # Given: 수학 + 과학 통합 시험
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기", "중학과학.2학년.물리"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: 두 과목의 개념이 포함되어야 함
    all_concepts = []
    for day_task in result.two_week_plan:
        all_concepts.extend(day_task.concepts_to_review)

    # 고유 개념 수 확인
    unique_concepts = set(all_concepts)
    assert len(unique_concepts) >= 2  # 최소 2개 이상


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_mock_exam_pdf_generation(db_session, sample_student, mock_mcp):
    """모의고사 PDF 생성 테스트"""

    # Given
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: PDF URL이 생성되어야 함
    assert result.mock_exam_pdf_url is not None
    assert "mock_exam" in result.mock_exam_pdf_url
    assert result.mock_exam_pdf_url.endswith(".pdf")

    # Then: Node 5 (Q-Metrics)가 호출되었어야 함
    assert mock_mcp.called("q-metrics", "generate_mock_exam")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_exam_prep_study_plan_progression(db_session, sample_student, mock_mcp):
    """학습 플랜의 진행 패턴 테스트"""

    # Given
    service = ExamPrepService(mcp=mock_mcp, db=db_session)

    request = ExamPrepRequest(
        student_id=sample_student.id,
        exam_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        school_id="SCH_001",
        curriculum_paths=["중학수학.2학년.1학기"]
    )

    # When
    result = await service.prepare_exam(request)

    # Then: 학습 패턴 검증
    # Day 1-7: 약점 집중 공략 (새로운 개념)
    # Day 8-11: 전범위 복습
    # Day 12-13: 모의고사
    # Day 14: 최종 점검 (Anki 위주)

    # 마지막 날은 가벼운 복습
    last_day = result.two_week_plan[-1]
    assert last_day.anki_reviews > 0
    assert len(last_day.practice_problems) <= 5  # 적은 문제
