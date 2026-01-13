"""
Custom Tool Repository (Real SQLAlchemy Implementation)

TDD 기반으로 구현된 실제 데이터베이스 Repository
커스텀 MCP Tool 관리
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from datetime import datetime
import uuid

from app.models.custom_tool import CustomTool


class CustomToolRepository:
    """커스텀 Tool Repository - SQLAlchemy Async 구현"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        name: str,
        description: str,
        input_schema: str,
        definition: dict,
        created_by: str,
        is_active: bool = True,
        tool_id: Optional[str] = None
    ) -> CustomTool:
        """
        커스텀 툴 생성

        Args:
            name: 툴 이름 (유니크)
            description: 툴 설명
            input_schema: 입력 스키마 (JSON 문자열)
            definition: 툴 정의 (JSON)
            created_by: 생성자 ID
            is_active: 활성 여부
            tool_id: 툴 ID (선택사항)

        Returns:
            생성된 CustomTool 객체
        """
        if tool_id is None:
            tool_id = f"ct_{uuid.uuid4().hex[:16]}"

        tool = CustomTool(
            id=tool_id,
            name=name,
            description=description,
            input_schema=input_schema,
            definition=definition,
            created_by=created_by,
            is_active=is_active,
            created_at=datetime.utcnow()
        )

        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)

        return tool

    async def get_by_id(self, tool_id: str) -> Optional[CustomTool]:
        """
        ID로 커스텀 툴 조회

        Args:
            tool_id: 툴 ID

        Returns:
            CustomTool 객체 또는 None
        """
        result = await self.db.execute(
            select(CustomTool).where(CustomTool.id == tool_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[CustomTool]:
        """
        이름으로 커스텀 툴 조회

        Args:
            name: 툴 이름

        Returns:
            CustomTool 객체 또는 None
        """
        result = await self.db.execute(
            select(CustomTool).where(CustomTool.name == name)
        )
        return result.scalar_one_or_none()

    async def list_by_creator(
        self,
        created_by: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CustomTool]:
        """
        생성자별 커스텀 툴 목록 조회

        Args:
            created_by: 생성자 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수

        Returns:
            CustomTool 객체 리스트
        """
        result = await self.db.execute(
            select(CustomTool)
            .where(CustomTool.created_by == created_by)
            .order_by(CustomTool.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_active_tools(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CustomTool]:
        """
        활성 커스텀 툴 목록 조회

        Args:
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수

        Returns:
            활성 CustomTool 객체 리스트
        """
        result = await self.db.execute(
            select(CustomTool)
            .where(CustomTool.is_active == True)
            .order_by(CustomTool.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        tool_id: str,
        description: Optional[str] = None,
        input_schema: Optional[str] = None,
        definition: Optional[dict] = None,
        is_active: Optional[bool] = None
    ) -> Optional[CustomTool]:
        """
        커스텀 툴 정보 수정

        Note: name은 유니크 제약이 있으므로 수정 불가

        Args:
            tool_id: 툴 ID
            description: 새 설명
            input_schema: 새 입력 스키마
            definition: 새 툴 정의
            is_active: 활성 여부

        Returns:
            수정된 CustomTool 객체 또는 None
        """
        # 툴 존재 확인
        tool = await self.get_by_id(tool_id)
        if tool is None:
            return None

        # 업데이트할 필드 준비
        update_data = {}
        if description is not None:
            update_data["description"] = description
        if input_schema is not None:
            update_data["input_schema"] = input_schema
        if definition is not None:
            update_data["definition"] = definition
        if is_active is not None:
            update_data["is_active"] = is_active

        # 업데이트 수행
        if update_data:
            stmt = (
                update(CustomTool)
                .where(CustomTool.id == tool_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()

            # 갱신된 객체 조회
            tool = await self.get_by_id(tool_id)

        return tool

    async def delete(self, tool_id: str) -> bool:
        """
        커스텀 툴 삭제

        Args:
            tool_id: 툴 ID

        Returns:
            삭제 성공 여부
        """
        # 툴 존재 확인
        tool = await self.get_by_id(tool_id)
        if tool is None:
            return False

        # 삭제 수행
        stmt = delete(CustomTool).where(CustomTool.id == tool_id)
        await self.db.execute(stmt)
        await self.db.commit()

        return True

    async def count_by_creator(self, created_by: str) -> int:
        """
        생성자별 커스텀 툴 수 카운트

        Args:
            created_by: 생성자 ID

        Returns:
            툴 수
        """
        result = await self.db.execute(
            select(func.count(CustomTool.id))
            .where(CustomTool.created_by == created_by)
        )
        return result.scalar() or 0

    async def exists_by_name(self, name: str) -> bool:
        """
        이름으로 커스텀 툴 존재 여부 확인

        Args:
            name: 툴 이름

        Returns:
            존재 여부
        """
        result = await self.db.execute(
            select(func.count(CustomTool.id))
            .where(CustomTool.name == name)
        )
        count = result.scalar() or 0
        return count > 0
