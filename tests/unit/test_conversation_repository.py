"""
Conversation Repository Tests (TDD - RED Phase)

ConversationRepository 및 MessageRepository CRUD 테스트
Conversation과 Message의 관계 테스트
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conversation_repository import ConversationRepository
from app.models.conversation import Conversation, Message


@pytest.mark.asyncio
async def test_create_conversation(db_session: AsyncSession):
    """대화 생성 테스트"""
    repo = ConversationRepository(db_session)

    conversation = await repo.create_conversation(
        student_id="student_test_001",
        title="테스트 대화"
    )

    assert conversation.id is not None
    assert conversation.student_id == "student_test_001"
    assert conversation.title == "테스트 대화"
    assert conversation.created_at is not None
    assert conversation.updated_at is not None


@pytest.mark.asyncio
async def test_get_conversation_by_id(db_session: AsyncSession):
    """대화 조회 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성
    created = await repo.create_conversation(
        student_id="student_test_002",
        title="조회 테스트 대화"
    )

    # When: ID로 조회
    found = await repo.get_conversation_by_id(created.id)

    # Then
    assert found is not None
    assert found.id == created.id
    assert found.title == "조회 테스트 대화"


@pytest.mark.asyncio
async def test_list_conversations_by_student(db_session: AsyncSession):
    """학생별 대화 목록 조회 테스트"""
    repo = ConversationRepository(db_session)

    student_id = "student_conv_list"

    # Given: 동일 학생의 대화 3개 생성
    await repo.create_conversation(student_id, "대화1")
    await repo.create_conversation(student_id, "대화2")
    await repo.create_conversation(student_id, "대화3")

    # When: 학생별 대화 목록 조회
    conversations = await repo.list_conversations_by_student(student_id)

    # Then
    assert len(conversations) >= 3
    titles = [c.title for c in conversations]
    assert "대화1" in titles
    assert "대화2" in titles
    assert "대화3" in titles


@pytest.mark.asyncio
async def test_update_conversation_title(db_session: AsyncSession):
    """대화 제목 수정 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성
    conversation = await repo.create_conversation(
        student_id="student_update",
        title="원래 제목"
    )
    original_id = conversation.id

    # When: 제목 수정
    updated = await repo.update_conversation(
        conversation_id=conversation.id,
        title="수정된 제목"
    )

    # Then
    assert updated is not None
    assert updated.id == original_id
    assert updated.title == "수정된 제목"
    assert updated.student_id == "student_update"


@pytest.mark.asyncio
async def test_delete_conversation(db_session: AsyncSession):
    """대화 삭제 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성
    conversation = await repo.create_conversation(
        student_id="student_delete",
        title="삭제될 대화"
    )
    conv_id = conversation.id

    # When: 삭제
    deleted = await repo.delete_conversation(conv_id)

    # Then
    assert deleted is True

    # 조회 시 없어야 함
    found = await repo.get_conversation_by_id(conv_id)
    assert found is None


@pytest.mark.asyncio
async def test_add_message_to_conversation(db_session: AsyncSession):
    """대화에 메시지 추가 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성
    conversation = await repo.create_conversation(
        student_id="student_msg",
        title="메시지 테스트 대화"
    )

    # When: 메시지 추가
    message = await repo.add_message(
        conversation_id=conversation.id,
        role="user",
        content="안녕하세요, 수학 문제를 풀어주세요."
    )

    # Then
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "안녕하세요, 수학 문제를 풀어주세요."
    assert message.created_at is not None


@pytest.mark.asyncio
async def test_get_messages_by_conversation(db_session: AsyncSession):
    """대화의 메시지 목록 조회 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성 및 메시지 3개 추가
    conversation = await repo.create_conversation(
        student_id="student_msg_list",
        title="메시지 목록 테스트"
    )

    await repo.add_message(conversation.id, "user", "첫 번째 메시지")
    await repo.add_message(conversation.id, "assistant", "두 번째 메시지")
    await repo.add_message(conversation.id, "user", "세 번째 메시지")

    # When: 메시지 목록 조회
    messages = await repo.get_messages_by_conversation(conversation.id)

    # Then
    assert len(messages) >= 3
    assert messages[0].content == "첫 번째 메시지"
    assert messages[0].role == "user"
    assert messages[1].content == "두 번째 메시지"
    assert messages[1].role == "assistant"
    assert messages[2].content == "세 번째 메시지"


@pytest.mark.asyncio
async def test_conversation_with_messages_relationship(db_session: AsyncSession):
    """대화-메시지 관계 테스트 (ORM relationship)"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성 및 메시지 추가
    conversation = await repo.create_conversation(
        student_id="student_rel",
        title="관계 테스트"
    )

    await repo.add_message(conversation.id, "user", "메시지1")
    await repo.add_message(conversation.id, "assistant", "메시지2")

    # When: 대화 조회 (with messages relationship)
    found = await repo.get_conversation_with_messages(conversation.id)

    # Then
    assert found is not None
    assert len(found.messages) >= 2
    assert found.messages[0].content == "메시지1"
    assert found.messages[1].content == "메시지2"


@pytest.mark.asyncio
async def test_delete_message(db_session: AsyncSession):
    """메시지 삭제 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 및 메시지 생성
    conversation = await repo.create_conversation(
        student_id="student_del_msg",
        title="메시지 삭제 테스트"
    )

    message = await repo.add_message(
        conversation.id,
        "user",
        "삭제될 메시지"
    )
    msg_id = message.id

    # When: 메시지 삭제
    deleted = await repo.delete_message(msg_id)

    # Then
    assert deleted is True

    # 메시지 목록에서 없어야 함
    messages = await repo.get_messages_by_conversation(conversation.id)
    message_ids = [m.id for m in messages]
    assert msg_id not in message_ids


@pytest.mark.asyncio
async def test_update_message_content(db_session: AsyncSession):
    """메시지 내용 수정 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 및 메시지 생성
    conversation = await repo.create_conversation(
        student_id="student_update_msg",
        title="메시지 수정 테스트"
    )

    message = await repo.add_message(
        conversation.id,
        "assistant",
        "원래 내용"
    )
    original_id = message.id

    # When: 메시지 내용 수정
    updated = await repo.update_message(
        message_id=message.id,
        content="수정된 내용"
    )

    # Then
    assert updated is not None
    assert updated.id == original_id
    assert updated.content == "수정된 내용"
    assert updated.role == "assistant"  # role은 변경 안 됨


@pytest.mark.asyncio
async def test_count_messages_in_conversation(db_session: AsyncSession):
    """대화의 메시지 수 카운트 테스트"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성 및 메시지 5개 추가
    conversation = await repo.create_conversation(
        student_id="student_count_msg",
        title="메시지 카운트 테스트"
    )

    for i in range(5):
        await repo.add_message(
            conversation.id,
            "user" if i % 2 == 0 else "assistant",
            f"메시지 {i+1}"
        )

    # When: 메시지 수 카운트
    count = await repo.count_messages(conversation.id)

    # Then
    assert count >= 5


@pytest.mark.asyncio
async def test_delete_conversation_cascades_messages(db_session: AsyncSession):
    """대화 삭제 시 메시지도 함께 삭제되는지 테스트 (CASCADE)"""
    repo = ConversationRepository(db_session)

    # Given: 대화 생성 및 메시지 추가
    conversation = await repo.create_conversation(
        student_id="student_cascade",
        title="CASCADE 테스트"
    )

    msg1 = await repo.add_message(conversation.id, "user", "메시지1")
    msg2 = await repo.add_message(conversation.id, "assistant", "메시지2")

    msg1_id = msg1.id
    msg2_id = msg2.id
    conv_id = conversation.id

    # When: 대화 삭제
    await repo.delete_conversation(conv_id)

    # Then: 메시지도 함께 삭제되어야 함
    # (실제로는 DB의 CASCADE 설정에 따라 자동 삭제됨)
    messages = await repo.get_messages_by_conversation(conv_id)
    assert len(messages) == 0
