"""
E2E Test Fixtures

Playwright를 사용한 실제 브라우저 테스트를 위한 픽스처
"""
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import asyncio
import uvicorn
import multiprocessing
import time
import os
import tempfile
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.api_app import app
from app.db.session import get_db
from app.config import settings

# Import models
from app.models.student import Student
from app.models.student_attempt import StudentAttempt
from app.models.workflow_session import WorkflowSession


# E2E 테스트용 임시 DB 파일
E2E_DB_FILE = tempfile.mktemp(suffix=".db")
E2E_DB_URL = f"sqlite+aiosqlite:///{E2E_DB_FILE}"


async def init_e2e_db():
    """E2E 테스트 DB 초기화"""
    engine = create_async_engine(E2E_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def cleanup_e2e_db():
    """E2E 테스트 DB 정리"""
    if os.path.exists(E2E_DB_FILE):
        os.remove(E2E_DB_FILE)


def run_server(port: int, db_url: str):
    """백그라운드에서 FastAPI 서버 실행"""
    import os
    os.environ["DATABASE_URL"] = db_url

    # DB 의존성 오버라이드
    from app.db.session import async_session_maker
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    engine = create_async_engine(db_url, echo=False)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처 (세션 스코프)"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def api_server(event_loop):
    """E2E 테스트용 FastAPI 서버 시작/종료"""
    # DB 초기화
    event_loop.run_until_complete(init_e2e_db())

    port = 8888
    process = multiprocessing.Process(target=run_server, args=(port, E2E_DB_URL))
    process.start()

    # 서버 시작 대기
    time.sleep(3)

    yield f"http://127.0.0.1:{port}"

    # 서버 종료
    process.terminate()
    process.join()

    # DB 정리
    event_loop.run_until_complete(cleanup_e2e_db())


@pytest.fixture(scope="function")
def api_base_url(api_server):
    """API 베이스 URL"""
    return api_server


@pytest.fixture(scope="function")
def browser():
    """Playwright 브라우저 인스턴스 (동기 픽스처)"""
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture(scope="function")
def page(browser):
    """Playwright 페이지 객체 (동기 픽스처)"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()
