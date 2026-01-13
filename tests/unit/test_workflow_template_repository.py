"""
Workflow Template Repository Tests (TDD - RED Phase)

WorkflowTemplateRepository CRUD 및 쿼리 테스트
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.workflow_template_repository import WorkflowTemplateRepository
from app.models.workflow_template import WorkflowTemplate


@pytest.mark.asyncio
async def test_create_workflow_template(db_session: AsyncSession):
    """워크플로우 템플릿 생성 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    template_definition = {
        "nodes": [
            {"id": "node1", "type": "tool", "tool_name": "get_student_profile"}
        ],
        "edges": []
    }

    template = await repo.create(
        name="테스트 워크플로우",
        description="테스트용 워크플로우 템플릿",
        definition=template_definition,
        created_by="teacher_001",
        is_public=True
    )

    assert template.id is not None
    assert template.name == "테스트 워크플로우"
    assert template.description == "테스트용 워크플로우 템플릿"
    assert template.definition == template_definition
    assert template.created_by == "teacher_001"
    assert template.is_public is True
    assert template.is_active is True
    assert template.execution_count == 0
    assert template.created_at is not None


@pytest.mark.asyncio
async def test_get_workflow_template_by_id(db_session: AsyncSession):
    """워크플로우 템플릿 조회 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 템플릿 생성
    created = await repo.create(
        name="조회 테스트",
        description="조회용 템플릿",
        definition={"nodes": [], "edges": []},
        created_by="teacher_002"
    )

    # When: ID로 조회
    found = await repo.get_by_id(created.id)

    # Then
    assert found is not None
    assert found.id == created.id
    assert found.name == "조회 테스트"


@pytest.mark.asyncio
async def test_get_workflow_template_by_id_not_found(db_session: AsyncSession):
    """존재하지 않는 템플릿 조회 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # When: 존재하지 않는 ID 조회
    found = await repo.get_by_id("nonexistent_id")

    # Then: None 반환
    assert found is None


@pytest.mark.asyncio
async def test_list_templates_by_creator(db_session: AsyncSession):
    """생성자별 템플릿 목록 조회 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    creator_id = "teacher_list_test"

    # Given: 동일 생성자의 템플릿 3개 생성
    await repo.create(
        name="템플릿1",
        description="desc1",
        definition={"nodes": [], "edges": []},
        created_by=creator_id
    )
    await repo.create(
        name="템플릿2",
        description="desc2",
        definition={"nodes": [], "edges": []},
        created_by=creator_id
    )
    await repo.create(
        name="템플릿3",
        description="desc3",
        definition={"nodes": [], "edges": []},
        created_by=creator_id
    )

    # When: 생성자별 템플릿 조회
    templates = await repo.list_by_creator(creator_id)

    # Then
    assert len(templates) >= 3
    names = [t.name for t in templates]
    assert "템플릿1" in names
    assert "템플릿2" in names
    assert "템플릿3" in names


@pytest.mark.asyncio
async def test_list_public_templates(db_session: AsyncSession):
    """공개 템플릿 목록 조회 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 공개/비공개 템플릿 생성
    await repo.create(
        name="공개템플릿1",
        description="public",
        definition={"nodes": [], "edges": []},
        created_by="creator_public",
        is_public=True
    )
    await repo.create(
        name="비공개템플릿",
        description="private",
        definition={"nodes": [], "edges": []},
        created_by="creator_public",
        is_public=False
    )
    await repo.create(
        name="공개템플릿2",
        description="public",
        definition={"nodes": [], "edges": []},
        created_by="creator_public",
        is_public=True
    )

    # When: 공개 템플릿만 조회
    public_templates = await repo.list_public_templates()

    # Then
    assert len(public_templates) >= 2
    for template in public_templates:
        assert template.is_public is True


@pytest.mark.asyncio
async def test_list_active_templates(db_session: AsyncSession):
    """활성 템플릿 목록 조회 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 활성/비활성 템플릿 생성
    active1 = await repo.create(
        name="활성템플릿1",
        description="active",
        definition={"nodes": [], "edges": []},
        created_by="creator_active",
        is_active=True
    )
    inactive = await repo.create(
        name="비활성템플릿",
        description="inactive",
        definition={"nodes": [], "edges": []},
        created_by="creator_active",
        is_active=False
    )

    # When: 활성 템플릿만 조회
    active_templates = await repo.list_by_creator(
        created_by="creator_active",
        only_active=True
    )

    # Then
    active_names = [t.name for t in active_templates]
    assert "활성템플릿1" in active_names
    assert "비활성템플릿" not in active_names


@pytest.mark.asyncio
async def test_update_workflow_template(db_session: AsyncSession):
    """워크플로우 템플릿 수정 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 템플릿 생성
    template = await repo.create(
        name="원래이름",
        description="원래설명",
        definition={"nodes": [], "edges": []},
        created_by="teacher_update"
    )
    original_id = template.id

    # When: 이름과 설명 수정
    updated = await repo.update(
        template_id=template.id,
        name="수정된이름",
        description="수정된설명",
        is_public=True
    )

    # Then
    assert updated is not None
    assert updated.id == original_id
    assert updated.name == "수정된이름"
    assert updated.description == "수정된설명"
    assert updated.is_public is True


@pytest.mark.asyncio
async def test_delete_workflow_template(db_session: AsyncSession):
    """워크플로우 템플릿 삭제 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 템플릿 생성
    template = await repo.create(
        name="삭제될템플릿",
        description="삭제용",
        definition={"nodes": [], "edges": []},
        created_by="teacher_delete"
    )
    template_id = template.id

    # When: 삭제
    deleted = await repo.delete(template_id)

    # Then
    assert deleted is True

    # 조회 시 없어야 함
    found = await repo.get_by_id(template_id)
    assert found is None


@pytest.mark.asyncio
async def test_increment_execution_count(db_session: AsyncSession):
    """실행 카운트 증가 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 템플릿 생성
    template = await repo.create(
        name="실행카운트테스트",
        description="execution count",
        definition={"nodes": [], "edges": []},
        created_by="teacher_exec"
    )
    assert template.execution_count == 0

    # When: 실행 카운트 증가
    await repo.increment_execution_count(template.id)

    # Then: 카운트가 1 증가
    updated = await repo.get_by_id(template.id)
    assert updated.execution_count == 1
    assert updated.last_executed_at is not None

    # When: 한 번 더 증가
    await repo.increment_execution_count(template.id)

    # Then: 카운트가 2
    updated = await repo.get_by_id(template.id)
    assert updated.execution_count == 2


@pytest.mark.asyncio
async def test_deactivate_template(db_session: AsyncSession):
    """템플릿 비활성화 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 활성 템플릿 생성
    template = await repo.create(
        name="비활성화테스트",
        description="deactivate",
        definition={"nodes": [], "edges": []},
        created_by="teacher_deactivate",
        is_active=True
    )
    assert template.is_active is True

    # When: 비활성화
    deactivated = await repo.update(
        template_id=template.id,
        is_active=False
    )

    # Then
    assert deactivated.is_active is False


@pytest.mark.asyncio
async def test_search_templates_by_name(db_session: AsyncSession):
    """템플릿 이름 검색 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    # Given: 다양한 이름의 템플릿 생성
    await repo.create(
        name="주간 진단 워크플로우",
        description="weekly",
        definition={"nodes": [], "edges": []},
        created_by="teacher_search"
    )
    await repo.create(
        name="오답 복습 워크플로우",
        description="error review",
        definition={"nodes": [], "edges": []},
        created_by="teacher_search"
    )
    await repo.create(
        name="학습 경로 생성",
        description="learning path",
        definition={"nodes": [], "edges": []},
        created_by="teacher_search"
    )

    # When: "워크플로우" 검색
    results = await repo.search_by_name("워크플로우")

    # Then
    assert len(results) >= 2
    names = [t.name for t in results]
    assert any("주간 진단" in name for name in names)
    assert any("오답 복습" in name for name in names)


@pytest.mark.asyncio
async def test_count_templates_by_creator(db_session: AsyncSession):
    """생성자별 템플릿 수 카운트 테스트"""
    repo = WorkflowTemplateRepository(db_session)

    creator_id = "teacher_count"

    # Given: 특정 생성자의 템플릿 3개 생성
    await repo.create(
        name="카운트1",
        description="c1",
        definition={"nodes": [], "edges": []},
        created_by=creator_id
    )
    await repo.create(
        name="카운트2",
        description="c2",
        definition={"nodes": [], "edges": []},
        created_by=creator_id
    )
    await repo.create(
        name="카운트3",
        description="c3",
        definition={"nodes": [], "edges": []},
        created_by=creator_id
    )

    # When: 생성자별 카운트
    count = await repo.count_by_creator(creator_id)

    # Then
    assert count >= 3
