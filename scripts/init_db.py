"""
데이터베이스 초기화 스크립트

테이블을 생성하고 초기 데이터를 설정합니다.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.db.base import Base
from app.models.student import Student
from app.models.workflow_session import WorkflowSession


async def init_db():
    """데이터베이스 테이블 생성"""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        future=True
    )

    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("✅ Database initialized successfully!")


async def init_test_db():
    """테스트 데이터베이스 테이블 생성"""
    print(f"\nInitializing test database: {settings.TEST_DATABASE_URL}")

    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("✅ Test database initialized successfully!")


if __name__ == "__main__":
    print("=== Database Initialization ===\n")

    # Main database
    asyncio.run(init_db())

    # Test database
    asyncio.run(init_test_db())

    print("\n=== All databases ready! ===")
