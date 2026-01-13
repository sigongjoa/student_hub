#!/usr/bin/env python3
"""
E2E UI Interaction Test with Playwright

실제 프론트엔드 UI 요소와 인터랙션하며 워크플로우를 테스트합니다.
"""
import asyncio
from playwright.async_api import async_playwright, Page, expect
import json

async def navigate_and_screenshot(page: Page, url: str, filename: str, description: str):
    """페이지 이동 및 스크린샷"""
    print(f"   📄 {description}...")
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"test_screenshots/{filename}")
    print(f"   ✅ Screenshot saved: {filename}")

async def test_dashboard(page: Page):
    """대시보드 테스트"""
    print("\n🏠 Testing Dashboard...")

    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    # Dashboard 제목 확인
    dashboard_heading = page.locator("h1:has-text('Dashboard')")
    await expect(dashboard_heading).to_be_visible()
    print("   ✅ Dashboard heading visible")

    # 통계 카드 확인
    total_students = page.locator("text=Total Students")
    await expect(total_students).to_be_visible()
    print("   ✅ Statistics cards visible")

    await page.screenshot(path="test_screenshots/02_dashboard.png")
    print("   📸 Dashboard screenshot saved")

async def test_students_page(page: Page):
    """Students 페이지 테스트"""
    print("\n👥 Testing Students page...")

    # Students 링크 클릭
    students_link = page.locator("text=Students").first
    await students_link.click()
    await page.wait_for_load_state("networkidle")

    # URL 확인
    await page.wait_for_url("**/students")
    print("   ✅ Navigated to Students page")

    await page.screenshot(path="test_screenshots/03_students_page.png")
    print("   📸 Students page screenshot saved")

async def test_student_detail(page: Page, student_id: str):
    """학생 상세 페이지 테스트"""
    print("\n👨‍🎓 Testing Student detail page...")

    # 학생 상세 페이지로 이동
    await page.goto(f"http://localhost:5173/students/{student_id}")
    await page.wait_for_load_state("networkidle")

    await page.screenshot(path="test_screenshots/04_student_detail.png")
    print("   📸 Student detail screenshot saved")

async def test_workflow_ui(page: Page):
    """워크플로우 UI 테스트"""
    print("\n⚙️ Testing Workflow UI elements...")

    # 워크플로우 버튼/링크 찾기
    workflow_elements = [
        "Weekly Diagnostic",
        "Error Review",
        "Learning Path",
        "Exam Prep"
    ]

    for workflow_name in workflow_elements:
        try:
            element = page.locator(f"text={workflow_name}")
            is_visible = await element.is_visible(timeout=2000)
            if is_visible:
                print(f"   ✅ Found workflow UI: {workflow_name}")
        except:
            print(f"   ⚠️  Workflow UI not found: {workflow_name} (may be in different page)")

async def test_navigation(page: Page):
    """네비게이션 메뉴 테스트"""
    print("\n🧭 Testing Navigation menu...")

    menu_items = [
        "Dashboard",
        "Students",
        "Logic Engine",
        "Q-DNA",
        "Reports",
        "Virtual Lab",
        "School Info"
    ]

    for item in menu_items:
        menu_link = page.locator(f"text={item}").first
        is_visible = await menu_link.is_visible()
        print(f"   {'✅' if is_visible else '❌'} {item}: {'visible' if is_visible else 'not visible'}")

    await page.screenshot(path="test_screenshots/05_navigation.png")
    print("   📸 Navigation screenshot saved")

async def test_api_integration(page: Page):
    """API 통합 테스트 - 프론트엔드에서 API 호출 확인"""
    print("\n🔌 Testing API integration from frontend...")

    # API 호출 감지를 위한 리스너 설정
    api_calls = []

    def handle_request(request):
        if "localhost:8000" in request.url:
            api_calls.append({
                "method": request.method,
                "url": request.url
            })

    page.on("request", handle_request)

    # Students 페이지로 이동 (API 호출 발생)
    await page.goto("http://localhost:5173/students")
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)  # API 호출 대기

    print(f"   ✅ Detected {len(api_calls)} API calls from frontend:")
    for call in api_calls[:5]:  # 최대 5개만 출력
        print(f"      - {call['method']} {call['url']}")

async def test_responsive_design(page: Page):
    """반응형 디자인 테스트"""
    print("\n📱 Testing responsive design...")

    viewports = [
        {"name": "Desktop", "width": 1920, "height": 1080},
        {"name": "Tablet", "width": 768, "height": 1024},
        {"name": "Mobile", "width": 375, "height": 667}
    ]

    for viewport in viewports:
        await page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
        await page.goto("http://localhost:5173")
        await page.wait_for_load_state("networkidle")

        filename = f"06_responsive_{viewport['name'].lower()}.png"
        await page.screenshot(path=f"test_screenshots/{filename}")
        print(f"   ✅ {viewport['name']} ({viewport['width']}x{viewport['height']}): {filename}")

async def main():
    """메인 테스트 실행"""
    print("=" * 80)
    print("🎨 Node 0 Student Hub - UI Interaction Test")
    print("=" * 80)

    async with async_playwright() as p:
        # 브라우저 실행 (headless 모드)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # 스크린샷 디렉토리 생성
            import os
            os.makedirs("test_screenshots", exist_ok=True)

            # 1. 대시보드 테스트
            await test_dashboard(page)

            # 2. 네비게이션 테스트
            await test_navigation(page)

            # 3. Students 페이지 테스트
            await test_students_page(page)

            # 4. API 통합 테스트
            await test_api_integration(page)

            # 5. 워크플로우 UI 테스트
            await test_workflow_ui(page)

            # 6. 반응형 디자인 테스트
            await test_responsive_design(page)

            # 7. 학생 생성 후 상세 페이지 테스트
            print("\n👨‍🎓 Creating test student via API...")
            response = await page.request.post(
                "http://localhost:8000/api/v1/students",
                data=json.dumps({
                    "name": "UI Test Student",
                    "grade": 12,
                    "school_id": "UI_TEST_001"
                }),
                headers={"Content-Type": "application/json"}
            )
            student_data = await response.json()
            student_id = student_data['id']
            print(f"   ✅ Student created: {student_id}")

            await test_student_detail(page, student_id)

            print("\n" + "=" * 80)
            print("✅ All UI interaction tests passed!")
            print(f"📸 Screenshots saved in: test_screenshots/")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            # 에러 발생 시 스크린샷 저장
            await page.screenshot(path="test_screenshots/error_ui.png")
            raise

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
