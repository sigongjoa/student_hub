"""
Integration Test Fixtures

실제 FastAPI 앱과 DB를 사용하는 통합 테스트용 픽스처
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.api_app import app
from app.db.session import get_db

# Import all models
from app.models.student import Student
from app.models.student_attempt import StudentAttempt
from app.models.workflow_session import WorkflowSession

# Import MockMCPManager from parent conftest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.conftest import MockMCPManager


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """통합 테스트용 인메모리 DB 엔진"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """통합 테스트용 DB 세션"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def api_client(db_session):
    """
    통합 테스트용 HTTP 클라이언트

    실제 FastAPI 앱을 구동하고 테스트 DB와 Mock MCP를 주입
    """
    # DB 세션 의존성 오버라이드
    async def override_get_db():
        yield db_session

    # MCP Manager 의존성 오버라이드
    mock_mcp_manager = MockMCPManager()

    def override_get_mcp_manager():
        return mock_mcp_manager

    # Import the dependency function from routers
    from app.routers.workflows import get_mcp_manager

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mcp_manager] = override_get_mcp_manager

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # 정리
    app.dependency_overrides.clear()
