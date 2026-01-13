"""
Student Repository (Real SQLAlchemy Implementation)

TDD 기반으로 구현된 실제 데이터베이스 Repository
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.future import select as future_select
from datetime import datetime
import uuid

from app.models.student import Student


class StudentRepository:
    """학생 Repository - SQLAlchemy Async 구현"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        name: str,
        grade: int,
        school_id: str,
        student_id: Optional[str] = None
    ) -> Student:
        """
        학생 생성

        Args:
            name: 학생 이름
            grade: 학년
            school_id: 학교 ID
            student_id: 학생 ID (선택사항, 없으면 자동 생성)

        Returns:
            생성된 Student 객체
        """
        if student_id is None:
            student_id = f"student_{uuid.uuid4().hex[:16]}"

        student = Student(
            id=student_id,
            name=name,
            grade=grade,
            school_id=school_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)

        return student

    async def get_by_id(self, student_id: str) -> Optional[Student]:
        """
        ID로 학생 조회

        Args:
            student_id: 학생 ID

        Returns:
            Student 객체 또는 None
        """
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Student]:
        """
        모든 학생 조회

        Returns:
            Student 객체 리스트
        """
        result = await self.db.execute(select(Student))
        return list(result.scalars().all())

    async def list_students(
        self,
        skip: int = 0,
        limit: int = 100,
        school_id: Optional[str] = None,
        grade: Optional[int] = None
    ) -> List[Student]:
        """
        학생 목록 조회 (페이지네이션 및 필터링)

        Args:
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            school_id: 학교 ID 필터 (선택사항)
            grade: 학년 필터 (선택사항)

        Returns:
            Student 객체 리스트
        """
        query = select(Student)

        # 필터 적용
        if school_id is not None:
            query = query.where(Student.school_id == school_id)
        if grade is not None:
            query = query.where(Student.grade == grade)

        # 페이지네이션
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        student_id: str,
        name: Optional[str] = None,
        grade: Optional[int] = None,
        school_id: Optional[str] = None
    ) -> Optional[Student]:
        """
        학생 정보 수정

        Args:
            student_id: 학생 ID
            name: 새 이름 (선택사항)
            grade: 새 학년 (선택사항)
            school_id: 새 학교 ID (선택사항)

        Returns:
            수정된 Student 객체 또는 None
        """
        # 학생 존재 확인
        student = await self.get_by_id(student_id)
        if student is None:
            return None

        # 업데이트할 필드 준비
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if grade is not None:
            update_data["grade"] = grade
        if school_id is not None:
            update_data["school_id"] = school_id

        # 항상 updated_at 갱신
        update_data["updated_at"] = datetime.utcnow()

        # 업데이트 수행
        if update_data:
            stmt = (
                update(Student)
                .where(Student.id == student_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()

            # 갱신된 객체 조회
            student = await self.get_by_id(student_id)

        return student

    async def delete(self, student_id: str) -> bool:
        """
        학생 삭제

        Args:
            student_id: 학생 ID

        Returns:
            삭제 성공 여부
        """
        # 학생 존재 확인
        student = await self.get_by_id(student_id)
        if student is None:
            return False

        # 삭제 수행
        stmt = delete(Student).where(Student.id == student_id)
        await self.db.execute(stmt)
        await self.db.commit()

        return True

    async def count_by_school(self, school_id: str) -> int:
        """
        학교별 학생 수 카운트

        Args:
            school_id: 학교 ID

        Returns:
            학생 수
        """
        result = await self.db.execute(
            select(func.count(Student.id)).where(Student.school_id == school_id)
        )
        return result.scalar() or 0

    async def exists(self, student_id: str) -> bool:
        """
        학생 존재 여부 확인

        Args:
            student_id: 학생 ID

        Returns:
            존재 여부
        """
        result = await self.db.execute(
            select(func.count(Student.id)).where(Student.id == student_id)
        )
        count = result.scalar() or 0
        return count > 0
