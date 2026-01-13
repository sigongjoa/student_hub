"""
Conversation Repository (Real SQLAlchemy Implementation)

TDD 기반으로 구현된 실제 데이터베이스 Repository
Conversation과 Message의 관계를 관리합니다.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.models.conversation import Conversation, Message


class ConversationRepository:
    """대화 Repository - SQLAlchemy Async 구현"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Conversation CRUD ====================

    async def create_conversation(
        self,
        student_id: str,
        title: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """
        대화 생성

        Args:
            student_id: 학생 ID
            title: 대화 제목
            conversation_id: 대화 ID (선택사항, 없으면 자동 생성)

        Returns:
            생성된 Conversation 객체
        """
        if conversation_id is None:
            conversation_id = f"conv_{uuid.uuid4().hex[:16]}"

        conversation = Conversation(
            id=conversation_id,
            student_id=student_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_conversation_by_id(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        """
        대화 조회 (메시지 제외)

        Args:
            conversation_id: 대화 ID

        Returns:
            Conversation 객체 또는 None
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_with_messages(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        """
        대화 조회 (메시지 포함)

        Args:
            conversation_id: 대화 ID

        Returns:
            Conversation 객체 (messages 관계 로드됨) 또는 None
        """
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list_conversations_by_student(
        self,
        student_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """
        학생별 대화 목록 조회

        Args:
            student_id: 학생 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수

        Returns:
            Conversation 객체 리스트
        """
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.student_id == student_id)
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None
    ) -> Optional[Conversation]:
        """
        대화 제목 수정

        Args:
            conversation_id: 대화 ID
            title: 새 제목

        Returns:
            수정된 Conversation 객체 또는 None
        """
        # 대화 존재 확인
        conversation = await self.get_conversation_by_id(conversation_id)
        if conversation is None:
            return None

        # 업데이트할 필드 준비
        update_data = {"updated_at": datetime.utcnow()}
        if title is not None:
            update_data["title"] = title

        # 업데이트 수행
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(**update_data)
        )
        await self.db.execute(stmt)
        await self.db.commit()

        # 갱신된 객체 조회
        conversation = await self.get_conversation_by_id(conversation_id)
        return conversation

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        대화 삭제 (CASCADE로 메시지도 함께 삭제됨)

        Args:
            conversation_id: 대화 ID

        Returns:
            삭제 성공 여부
        """
        # 대화 존재 확인
        conversation = await self.get_conversation_by_id(conversation_id)
        if conversation is None:
            return False

        # ORM delete를 사용하여 cascade가 작동하도록 함
        await self.db.delete(conversation)
        await self.db.commit()

        return True

    # ==================== Message CRUD ====================

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Message:
        """
        메시지 추가

        Args:
            conversation_id: 대화 ID
            role: 메시지 역할 (user, assistant, system)
            content: 메시지 내용
            message_id: 메시지 ID (선택사항)
            metadata: 추가 메타데이터

        Returns:
            생성된 Message 객체
        """
        if message_id is None:
            message_id = f"msg_{uuid.uuid4().hex[:16]}"

        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=metadata or {},
            created_at=datetime.utcnow()
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_messages_by_conversation(
        self,
        conversation_id: str,
        skip: int = 0,
        limit: int = 1000
    ) -> List[Message]:
        """
        대화의 메시지 목록 조회 (시간순 정렬)

        Args:
            conversation_id: 대화 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수

        Returns:
            Message 객체 리스트
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_message(
        self,
        message_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[Message]:
        """
        메시지 내용 수정

        Args:
            message_id: 메시지 ID
            content: 새 내용
            metadata: 새 메타데이터

        Returns:
            수정된 Message 객체 또는 None
        """
        # 메시지 존재 확인
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if message is None:
            return None

        # 업데이트할 필드 준비
        update_data = {}
        if content is not None:
            update_data["content"] = content
        if metadata is not None:
            update_data["message_metadata"] = metadata

        # 업데이트 수행
        if update_data:
            stmt = (
                update(Message)
                .where(Message.id == message_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()

            # 갱신된 객체 조회
            result = await self.db.execute(
                select(Message).where(Message.id == message_id)
            )
            message = result.scalar_one_or_none()

        return message

    async def delete_message(self, message_id: str) -> bool:
        """
        메시지 삭제

        Args:
            message_id: 메시지 ID

        Returns:
            삭제 성공 여부
        """
        # 메시지 존재 확인
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if message is None:
            return False

        # 삭제 수행
        stmt = delete(Message).where(Message.id == message_id)
        await self.db.execute(stmt)
        await self.db.commit()

        return True

    async def count_messages(self, conversation_id: str) -> int:
        """
        대화의 메시지 수 카운트

        Args:
            conversation_id: 대화 ID

        Returns:
            메시지 수
        """
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        return result.scalar() or 0
