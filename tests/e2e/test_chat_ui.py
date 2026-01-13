"""
Chat UI E2E Tests with Screenshots

Playwright를 사용한 Chat UI 동작 검증 및 스크린샷 촬영
"""
import pytest
from playwright.async_api import async_playwright, Page
import asyncio
import os

# 스크린샷 저장 디렉토리
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "../../screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.mark.asyncio
async def test_chat_ui_initial_load():
    """
    Chat UI 초기 로드 스크린샷
    
    Given: Chat 테스트 페이지 접속
    When: 페이지가 로드됨
    Then: 초기 UI 스크린샷 촬영
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        # 페이지 접속
        await page.goto("http://localhost:8000/chat-test")
        
        # 페이지 로드 대기
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 스크린샷 촬영
        screenshot_path = os.path.join(SCREENSHOT_DIR, "01_chat_ui_initial_load.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # 기본 요소 확인
        header = await page.query_selector("h1")
        assert header is not None
        header_text = await header.inner_text()
        assert "Student Hub" in header_text
        
        await browser.close()


@pytest.mark.asyncio
async def test_chat_ui_user_message():
    """
    사용자 메시지 입력 스크린샷
    
    Given: Chat 페이지가 로드됨
    When: 사용자가 메시지를 입력함
    Then: 입력 상태 스크린샷 촬영
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        await page.goto("http://localhost:8000/chat-test")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 메시지 입력
        input_field = await page.query_selector("#messageInput")
        await input_field.fill("안녕하세요! 학생 관리 시스템에 대해 알려주세요.")
        await asyncio.sleep(0.5)
        
        # 스크린샷 촬영
        screenshot_path = os.path.join(SCREENSHOT_DIR, "02_chat_ui_user_input.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        await browser.close()


@pytest.mark.asyncio
async def test_chat_ui_conversation():
    """
    실제 대화 진행 스크린샷
    
    Given: Chat 페이지가 로드됨
    When: 사용자가 메시지를 전송하고 AI 응답을 받음
    Then: 대화 진행 스크린샷 촬영
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        await page.goto("http://localhost:8000/chat-test")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 첫 번째 메시지 전송
        input_field = await page.query_selector("#messageInput")
        await input_field.fill("안녕하세요!")
        
        send_button = await page.query_selector("#sendButton")
        await send_button.click()
        
        # AI 응답 대기 (최대 15초)
        await page.wait_for_selector(".message.assistant", timeout=15000)
        await asyncio.sleep(2)
        
        # 첫 번째 대화 스크린샷
        screenshot_path = os.path.join(SCREENSHOT_DIR, "03_chat_ui_first_message.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # 두 번째 메시지 전송
        await asyncio.sleep(1)
        await input_field.fill("학생 약점 분석 기능에 대해 설명해주세요.")
        await send_button.click()
        
        # AI 응답 대기
        await asyncio.sleep(8)
        
        # 두 번째 대화 스크린샷
        screenshot_path = os.path.join(SCREENSHOT_DIR, "04_chat_ui_multi_turn_conversation.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # 메시지 개수 확인
        user_messages = await page.query_selector_all(".message.user")
        assistant_messages = await page.query_selector_all(".message.assistant")
        
        assert len(user_messages) >= 2, "Should have at least 2 user messages"
        assert len(assistant_messages) >= 2, "Should have at least 2 assistant messages"
        
        await browser.close()


@pytest.mark.asyncio
async def test_chat_ui_streaming():
    """
    스트리밍 응답 스크린샷
    
    Given: Chat 페이지가 로드됨
    When: AI가 스트리밍으로 응답 중
    Then: 스트리밍 중간 단계 스크린샷 촬영
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        await page.goto("http://localhost:8000/chat-test")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 긴 응답을 유도하는 질문
        input_field = await page.query_selector("#messageInput")
        await input_field.fill("Node 0 Student Hub의 모든 기능을 자세히 설명해주세요.")
        
        send_button = await page.query_selector("#sendButton")
        await send_button.click()
        
        # 타이핑 인디케이터 대기
        await page.wait_for_selector("#typingIndicator", timeout=5000)
        await asyncio.sleep(0.5)
        
        # 타이핑 인디케이터 스크린샷
        screenshot_path = os.path.join(SCREENSHOT_DIR, "05_chat_ui_typing_indicator.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # 스트리밍 중간 단계 스크린샷
        await asyncio.sleep(3)
        screenshot_path = os.path.join(SCREENSHOT_DIR, "06_chat_ui_streaming_response.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # 완전한 응답 대기
        await asyncio.sleep(5)
        screenshot_path = os.path.join(SCREENSHOT_DIR, "07_chat_ui_complete_response.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        await browser.close()


@pytest.mark.asyncio
async def test_chat_ui_mobile_view():
    """
    모바일 뷰 스크린샷
    
    Given: 모바일 화면 크기로 Chat 페이지 접속
    When: 페이지가 로드됨
    Then: 모바일 UI 스크린샷 촬영
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # iPhone 13 Pro 화면 크기
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        
        await page.goto("http://localhost:8000/chat-test")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 모바일 초기 화면 스크린샷
        screenshot_path = os.path.join(SCREENSHOT_DIR, "08_chat_ui_mobile_initial.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # 모바일에서 메시지 전송
        input_field = await page.query_selector("#messageInput")
        await input_field.fill("안녕하세요!")
        
        send_button = await page.query_selector("#sendButton")
        await send_button.click()
        
        await page.wait_for_selector(".message.assistant", timeout=15000)
        await asyncio.sleep(2)
        
        # 모바일 대화 스크린샷
        screenshot_path = os.path.join(SCREENSHOT_DIR, "09_chat_ui_mobile_conversation.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        await browser.close()


if __name__ == "__main__":
    # 개별 실행을 위한 헬퍼
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        asyncio.run(globals()[test_name]())
    else:
        print("Usage: python test_chat_ui.py <test_function_name>")
        print("Example: python test_chat_ui.py test_chat_ui_initial_load")
