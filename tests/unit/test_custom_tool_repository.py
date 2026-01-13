"""
Custom Tool Repository Tests (TDD - RED Phase)

CustomToolRepository CRUD 및 쿼리 테스트
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.custom_tool_repository import CustomToolRepository
from app.models.custom_tool import CustomTool


@pytest.mark.asyncio
async def test_create_custom_tool(db_session: AsyncSession):
    """커스텀 툴 생성 테스트"""
    repo = CustomToolRepository(db_session)

    tool_definition = {
        "type": "http_request",
        "config": {
            "url": "https://api.example.com/data",
            "method": "GET"
        }
    }

    input_schema = '{"type": "object", "properties": {"param1": {"type": "string"}}}'

    tool = await repo.create(
        name="custom_api_call",
        description="커스텀 API 호출 툴",
        input_schema=input_schema,
        definition=tool_definition,
        created_by="teacher_001",
        is_active=True
    )

    assert tool.id is not None
    assert tool.name == "custom_api_call"
    assert tool.description == "커스텀 API 호출 툴"
    assert tool.input_schema == input_schema
    assert tool.definition == tool_definition
    assert tool.created_by == "teacher_001"
    assert tool.is_active is True
    assert tool.created_at is not None


@pytest.mark.asyncio
async def test_get_custom_tool_by_id(db_session: AsyncSession):
    """커스텀 툴 조회 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 툴 생성
    created = await repo.create(
        name="test_tool_get",
        description="조회 테스트 툴",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="teacher_002"
    )

    # When: ID로 조회
    found = await repo.get_by_id(created.id)

    # Then
    assert found is not None
    assert found.id == created.id
    assert found.name == "test_tool_get"


@pytest.mark.asyncio
async def test_get_custom_tool_by_name(db_session: AsyncSession):
    """커스텀 툴 이름으로 조회 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 툴 생성
    created = await repo.create(
        name="unique_tool_name",
        description="이름 조회 테스트",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="teacher_003"
    )

    # When: 이름으로 조회
    found = await repo.get_by_name("unique_tool_name")

    # Then
    assert found is not None
    assert found.id == created.id
    assert found.name == "unique_tool_name"


@pytest.mark.asyncio
async def test_get_custom_tool_by_name_not_found(db_session: AsyncSession):
    """존재하지 않는 이름으로 조회 테스트"""
    repo = CustomToolRepository(db_session)

    # When: 존재하지 않는 이름 조회
    found = await repo.get_by_name("nonexistent_tool")

    # Then: None 반환
    assert found is None


@pytest.mark.asyncio
async def test_list_tools_by_creator(db_session: AsyncSession):
    """생성자별 커스텀 툴 목록 조회 테스트"""
    repo = CustomToolRepository(db_session)

    creator_id = "teacher_list_test"

    # Given: 동일 생성자의 툴 3개 생성
    await repo.create(
        name="tool_1_list",
        description="툴1",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by=creator_id
    )
    await repo.create(
        name="tool_2_list",
        description="툴2",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by=creator_id
    )
    await repo.create(
        name="tool_3_list",
        description="툴3",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by=creator_id
    )

    # When: 생성자별 툴 조회
    tools = await repo.list_by_creator(creator_id)

    # Then
    assert len(tools) >= 3
    names = [t.name for t in tools]
    assert "tool_1_list" in names
    assert "tool_2_list" in names
    assert "tool_3_list" in names


@pytest.mark.asyncio
async def test_list_active_tools(db_session: AsyncSession):
    """활성 커스텀 툴 목록 조회 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 활성/비활성 툴 생성
    await repo.create(
        name="active_tool_1",
        description="활성 툴",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="creator_active",
        is_active=True
    )
    await repo.create(
        name="inactive_tool",
        description="비활성 툴",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="creator_active",
        is_active=False
    )

    # When: 활성 툴만 조회
    active_tools = await repo.list_active_tools()

    # Then
    active_names = [t.name for t in active_tools]
    assert "active_tool_1" in active_names
    assert "inactive_tool" not in active_names


@pytest.mark.asyncio
async def test_update_custom_tool(db_session: AsyncSession):
    """커스텀 툴 수정 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 툴 생성
    tool = await repo.create(
        name="tool_to_update",
        description="원래 설명",
        input_schema='{"type": "object"}',
        definition={"type": "old"},
        created_by="teacher_update"
    )
    original_id = tool.id

    # When: 설명과 정의 수정
    updated = await repo.update(
        tool_id=tool.id,
        description="수정된 설명",
        definition={"type": "new"},
        is_active=False
    )

    # Then
    assert updated is not None
    assert updated.id == original_id
    assert updated.name == "tool_to_update"  # 이름은 변경 안 됨
    assert updated.description == "수정된 설명"
    assert updated.definition == {"type": "new"}
    assert updated.is_active is False


@pytest.mark.asyncio
async def test_delete_custom_tool(db_session: AsyncSession):
    """커스텀 툴 삭제 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 툴 생성
    tool = await repo.create(
        name="tool_to_delete",
        description="삭제될 툴",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="teacher_delete"
    )
    tool_id = tool.id

    # When: 삭제
    deleted = await repo.delete(tool_id)

    # Then
    assert deleted is True

    # 조회 시 없어야 함
    found = await repo.get_by_id(tool_id)
    assert found is None


@pytest.mark.asyncio
async def test_deactivate_tool(db_session: AsyncSession):
    """커스텀 툴 비활성화 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 활성 툴 생성
    tool = await repo.create(
        name="tool_to_deactivate",
        description="비활성화 테스트",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="teacher_deactivate",
        is_active=True
    )
    assert tool.is_active is True

    # When: 비활성화
    deactivated = await repo.update(
        tool_id=tool.id,
        is_active=False
    )

    # Then
    assert deactivated.is_active is False


@pytest.mark.asyncio
async def test_tool_name_unique_constraint(db_session: AsyncSession):
    """툴 이름 유니크 제약 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 첫 번째 툴 생성
    await repo.create(
        name="unique_name_test",
        description="첫 번째",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="teacher_unique"
    )

    # When/Then: 동일한 이름으로 두 번째 툴 생성 시도 (예외 발생)
    with pytest.raises(Exception):  # IntegrityError 또는 다른 DB 예외
        await repo.create(
            name="unique_name_test",
            description="두 번째",
            input_schema='{"type": "object"}',
            definition={"type": "test"},
            created_by="teacher_unique"
        )


@pytest.mark.asyncio
async def test_count_tools_by_creator(db_session: AsyncSession):
    """생성자별 커스텀 툴 수 카운트 테스트"""
    repo = CustomToolRepository(db_session)

    creator_id = "teacher_count"

    # Given: 특정 생성자의 툴 3개 생성
    await repo.create(
        name="count_tool_1",
        description="c1",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by=creator_id
    )
    await repo.create(
        name="count_tool_2",
        description="c2",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by=creator_id
    )
    await repo.create(
        name="count_tool_3",
        description="c3",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by=creator_id
    )

    # When: 생성자별 카운트
    count = await repo.count_by_creator(creator_id)

    # Then
    assert count >= 3


@pytest.mark.asyncio
async def test_tool_exists(db_session: AsyncSession):
    """커스텀 툴 존재 여부 확인 테스트"""
    repo = CustomToolRepository(db_session)

    # Given: 툴 생성
    tool = await repo.create(
        name="exists_test_tool",
        description="존재 확인 테스트",
        input_schema='{"type": "object"}',
        definition={"type": "test"},
        created_by="teacher_exists"
    )

    # When/Then: 존재하는 툴
    exists = await repo.exists_by_name("exists_test_tool")
    assert exists is True

    # When/Then: 존재하지 않는 툴
    not_exists = await repo.exists_by_name("nonexistent_tool")
    assert not_exists is False
