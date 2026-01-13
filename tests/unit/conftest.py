"""
Unit Test Fixtures

Unit 테스트용 인메모리 SQLite 데이터베이스 픽스처
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base

# Import all models to register them with Base.metadata
from app.models.student import Student  # noqa: F401
from app.models.student_attempt import StudentAttempt  # noqa: F401
from app.models.workflow_session import WorkflowSession  # noqa: F401


@pytest.fixture(scope="function")
async def db_engine():
    """Unit 테스트용 인메모리 SQLite 엔진"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    # 모든 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Unit 테스트용 데이터베이스 세션"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()
