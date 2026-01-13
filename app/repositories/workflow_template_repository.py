"""
Workflow Template Repository (Real SQLAlchemy Implementation)

TDD 기반으로 구현된 실제 데이터베이스 Repository
워크플로우 템플릿 관리
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from datetime import datetime
import uuid

from app.models.workflow_template import WorkflowTemplate


class WorkflowTemplateRepository:
    """워크플로우 템플릿 Repository - SQLAlchemy Async 구현"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        name: str,
        description: Optional[str],
        definition: dict,
        created_by: str,
        is_public: bool = False,
        is_active: bool = True,
        template_id: Optional[str] = None
    ) -> WorkflowTemplate:
        """
        워크플로우 템플릿 생성

        Args:
            name: 템플릿 이름
            description: 템플릿 설명
            definition: 워크플로우 정의 (JSON)
            created_by: 생성자 ID
            is_public: 공개 여부
            is_active: 활성 여부
            template_id: 템플릿 ID (선택사항)

        Returns:
            생성된 WorkflowTemplate 객체
        """
        if template_id is None:
            template_id = f"wft_{uuid.uuid4().hex[:16]}"

        template = WorkflowTemplate(
            id=template_id,
            name=name,
            description=description,
            definition=definition,
            created_by=created_by,
            is_public=is_public,
            is_active=is_active,
            execution_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def get_by_id(self, template_id: str) -> Optional[WorkflowTemplate]:
        """
        ID로 템플릿 조회

        Args:
            template_id: 템플릿 ID

        Returns:
            WorkflowTemplate 객체 또는 None
        """
        result = await self.db.execute(
            select(WorkflowTemplate).where(WorkflowTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def list_by_creator(
        self,
        created_by: str,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = False
    ) -> List[WorkflowTemplate]:
        """
        생성자별 템플릿 목록 조회

        Args:
            created_by: 생성자 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            only_active: 활성 템플릿만 조회

        Returns:
            WorkflowTemplate 객체 리스트
        """
        query = select(WorkflowTemplate).where(
            WorkflowTemplate.created_by == created_by
        )

        if only_active:
            query = query.where(WorkflowTemplate.is_active == True)

        query = query.order_by(WorkflowTemplate.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_public_templates(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTemplate]:
        """
        공개 템플릿 목록 조회

        Args:
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수

        Returns:
            공개 WorkflowTemplate 객체 리스트
        """
        result = await self.db.execute(
            select(WorkflowTemplate)
            .where(WorkflowTemplate.is_public == True)
            .where(WorkflowTemplate.is_active == True)
            .order_by(WorkflowTemplate.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        definition: Optional[dict] = None,
        is_public: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> Optional[WorkflowTemplate]:
        """
        템플릿 정보 수정

        Args:
            template_id: 템플릿 ID
            name: 새 이름
            description: 새 설명
            definition: 새 워크플로우 정의
            is_public: 공개 여부
            is_active: 활성 여부

        Returns:
            수정된 WorkflowTemplate 객체 또는 None
        """
        # 템플릿 존재 확인
        template = await self.get_by_id(template_id)
        if template is None:
            return None

        # 업데이트할 필드 준비
        update_data = {"updated_at": datetime.utcnow()}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if definition is not None:
            update_data["definition"] = definition
        if is_public is not None:
            update_data["is_public"] = is_public
        if is_active is not None:
            update_data["is_active"] = is_active

        # 업데이트 수행
        if update_data:
            stmt = (
                update(WorkflowTemplate)
                .where(WorkflowTemplate.id == template_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()

            # 갱신된 객체 조회
            template = await self.get_by_id(template_id)

        return template

    async def delete(self, template_id: str) -> bool:
        """
        템플릿 삭제

        Args:
            template_id: 템플릿 ID

        Returns:
            삭제 성공 여부
        """
        # 템플릿 존재 확인
        template = await self.get_by_id(template_id)
        if template is None:
            return False

        # 삭제 수행
        stmt = delete(WorkflowTemplate).where(WorkflowTemplate.id == template_id)
        await self.db.execute(stmt)
        await self.db.commit()

        return True

    async def increment_execution_count(self, template_id: str) -> bool:
        """
        실행 카운트 증가

        Args:
            template_id: 템플릿 ID

        Returns:
            성공 여부
        """
        # 템플릿 존재 확인
        template = await self.get_by_id(template_id)
        if template is None:
            return False

        # 실행 카운트 증가
        stmt = (
            update(WorkflowTemplate)
            .where(WorkflowTemplate.id == template_id)
            .values(
                execution_count=WorkflowTemplate.execution_count + 1,
                last_executed_at=datetime.utcnow()
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

        return True

    async def search_by_name(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTemplate]:
        """
        이름으로 템플릿 검색

        Args:
            search_term: 검색어
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수

        Returns:
            검색된 WorkflowTemplate 객체 리스트
        """
        result = await self.db.execute(
            select(WorkflowTemplate)
            .where(WorkflowTemplate.name.ilike(f"%{search_term}%"))
            .order_by(WorkflowTemplate.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_creator(self, created_by: str) -> int:
        """
        생성자별 템플릿 수 카운트

        Args:
            created_by: 생성자 ID

        Returns:
            템플릿 수
        """
        result = await self.db.execute(
            select(func.count(WorkflowTemplate.id))
            .where(WorkflowTemplate.created_by == created_by)
        )
        return result.scalar() or 0
