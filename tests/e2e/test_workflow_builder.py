"""
Workflow Builder UI E2E Tests

Playwright를 사용한 Workflow Builder UI 스크린샷 촬영
"""
import pytest
from playwright.async_api import async_playwright
import asyncio
import os

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "../../screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.mark.asyncio
async def test_workflow_builder_initial():
    """Workflow Builder 초기 화면"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://localhost:8000/workflow-builder")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        screenshot_path = os.path.join(SCREENSHOT_DIR, "10_workflow_builder_initial.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        await browser.close()


@pytest.mark.asyncio
async def test_workflow_builder_with_nodes():
    """노드가 추가된 Workflow Builder"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://localhost:8000/workflow-builder")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 템플릿 정보 입력
        await page.fill("#template-name", "학생 약점 분석 워크플로우")
        await page.fill("#template-desc", "학생의 약점을 분석하고 학습 경로를 생성하는 워크플로우")
        
        # 캔버스로 드래그 시뮬레이션 (JavaScript 실행)
        await page.evaluate("""
            const canvas = document.getElementById('canvas');
            
            // 첫 번째 노드 추가 (약점 분석)
            createNode('analyze_student_weaknesses', 400, 200);
            
            // 두 번째 노드 추가 (학습 경로)
            createNode('generate_learning_path', 700, 200);
            
            // 세 번째 노드 추가 (시험 준비)
            createNode('prepare_exam', 1000, 200);
        """)
        
        await asyncio.sleep(1)
        
        screenshot_path = os.path.join(SCREENSHOT_DIR, "11_workflow_builder_with_nodes.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        await browser.close()


@pytest.mark.asyncio
async def test_workflow_builder_node_selected():
    """노드 선택 및 설정 화면"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://localhost:8000/workflow-builder")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # 템플릿 정보 입력
        await page.fill("#template-name", "맞춤형 학습 워크플로우")
        
        # 노드 추가 및 선택
        await page.evaluate("""
            createNode('get_student_profile', 500, 250);
        """)
        
        await asyncio.sleep(0.5)
        
        # 노드 클릭하여 선택
        await page.evaluate("""
            const node = document.getElementById('node1');
            if (node) node.click();
        """)
        
        await asyncio.sleep(1)
        
        screenshot_path = os.path.join(SCREENSHOT_DIR, "12_workflow_builder_node_config.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        await browser.close()
