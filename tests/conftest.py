"""
pytest 픽스처

gRPC 테스트, DB 세션, MCP 목 등 공통 픽스처를 제공합니다.
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.config import settings
from app.models.student import Student
from app.models.workflow_session import WorkflowSession


# Event Loop Fixture
@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 생성"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database Fixtures
@pytest.fixture(scope="function")
async def db_engine():
    """테스트용 비동기 엔진 생성"""
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,  # 테스트 시 SQL 로그 끄기
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """테스트용 DB 세션"""
    async_session_maker = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


# Mock MCP Client
class MockMCPResponse:
    """Mock MCP 응답"""
    def __init__(self, data):
        self.data = data


class MockMCPManager:
    """Mock MCP Client Manager"""

    def __init__(self):
        self.call_history = []

    async def call(self, node: str, tool: str, params: dict):
        """MCP 호출 목"""
        self.call_history.append({
            "node": node,
            "tool": tool,
            "params": params
        })

        # Mock responses for Weekly Diagnostic
        if node == "lab-node" and tool == "get_recent_concepts":
            return {
                "concepts": ["도함수", "적분", "극한"]
            }

        if node == "q-dna" and tool == "get_student_mastery":
            return {
                "도함수": 0.45,
                "적분": 0.55,
                "극한": 0.75
            }

        if node == "q-dna" and tool == "recommend_questions":
            return {
                "questions": [
                    {
                        "id": f"q_{i}",
                        "content": f"문제 {i}",
                        "difficulty": "medium",
                        "concepts": ["도함수"]
                    }
                    for i in range(10)
                ]
            }

        # Error Review 관련 응답
        if node == "q-dna" and tool == "get_question_dna":
            return {
                "question_id": params.get("question_id"),
                "difficulty": "medium",
                "concepts": ["이차함수", "최댓값", "도함수"],
                "bloom_level": "apply"
            }

        if node == "error-note" and tool == "create_error_note":
            import uuid
            return {
                "error_note_id": f"en_{uuid.uuid4().hex[:16]}",
                "created_at": "2026-01-10T13:00:00",
                "analysis": {
                    "misconception": "이차함수의 최댓값 개념 혼동",
                    "root_cause": "위로 볼록/아래로 볼록 판단 오류",
                    "related_concepts": ["이차함수", "도함수", "극값"]
                }
            }

        if node == "error-note" and tool == "calculate_anki_schedule":
            from datetime import datetime, timedelta
            return {
                "next_review_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "interval_days": 1,
                "ease_factor": 2.5
            }

        return {"status": "mock_response"}

    def called(self, node: str, tool: str) -> bool:
        """특정 MCP 호출이 있었는지 확인"""
        return any(
            call["node"] == node and call["tool"] == tool
            for call in self.call_history
        )

    async def initialize(self):
        """초기화 (mock)"""
        pass

    async def close_all(self):
        """종료 (mock)"""
        pass


@pytest.fixture
def mock_mcp():
    """Mock MCP Client Manager 픽스처"""
    return MockMCPManager()


# Sample Data Fixtures
@pytest.fixture
async def sample_student(db_session: AsyncSession):
    """샘플 학생 데이터"""
    student = Student(
        id="student_test123",
        name="테스트 학생",
        grade=10,
        school_id="SCH_001"
    )
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)
    return student


@pytest.fixture
async def sample_workflow_session(db_session: AsyncSession, sample_student):
    """샘플 워크플로우 세션"""
    session = WorkflowSession(
        workflow_id="wf_test123",
        student_id=sample_student.id,
        workflow_type="weekly_diagnostic",
        status="in_progress",
        workflow_metadata={"test": True}
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session
