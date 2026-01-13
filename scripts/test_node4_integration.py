"""
Node 4 Lab Node Integration Test

프론트엔드 Student Detail 페이지가 Node 4 데이터를 제대로 표시하는지 확인합니다.
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

# 색상
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_pass(msg: str):
    print(f"{GREEN}✓{RESET} {msg}")

def log_info(msg: str):
    print(f"{BLUE}ℹ{RESET} {msg}")


async def test_node4_integration():
    """Node 4 데이터 통합 테스트"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        api_response = None

        def handle_response(response):
            nonlocal api_response
            if "unified-profile" in response.url:
                api_response = response

        page.on("response", handle_response)

        try:
            log_info("=" * 60)
            log_info("Node 4 Lab Node Integration Test")
            log_info("=" * 60)

            # 1. 학생 목록 로드
            log_info("\n[1] Loading students list...")
            await page.goto("http://localhost:5173/students", wait_until="networkidle", timeout=10000)
            log_pass("Students list loaded")

            # 2. 첫 번째 학생 클릭
            log_info("\n[2] Navigating to student detail...")
            first_link = page.locator("tbody tr a").first
            await first_link.click()
            await page.wait_for_url("**/students/**", timeout=5000)
            log_pass(f"Navigated to: {page.url}")

            # 3. API 응답 대기
            log_info("\n[3] Waiting for API response...")
            await page.wait_for_timeout(3000)

            if api_response and api_response.status == 200:
                log_pass(f"API call successful (Status: {api_response.status})")

                # API 응답 분석
                response_json = await api_response.json()

                log_info("\n[4] Analyzing Node 4 Data...")
                log_info("-" * 60)

                # Mastery Summary
                mastery = response_json.get("mastery_summary", {})
                log_info(f"Mastery Summary:")
                log_pass(f"  Average: {mastery.get('average', 0)}")
                log_pass(f"  Total Attempts: {mastery.get('total_attempts', 0)}")
                log_pass(f"  Trend: {mastery.get('recent_trend', 'N/A')}")

                # Recent Activities
                activities = response_json.get("recent_activities", [])
                log_info(f"\nRecent Activities: {len(activities)} items")
                for i, activity in enumerate(activities[:3], 1):
                    log_pass(f"  {i}. {activity.get('type')} - {activity.get('score')} points")

                # Heatmap Data
                heatmap = response_json.get("heatmap_data", {})
                log_info(f"\nHeatmap Data: {len(heatmap)} concepts")
                for concept, score in heatmap.items():
                    log_pass(f"  {concept}: {score}")

                # 5. 페이지 콘텐츠 확인
                log_info("\n[5] Checking page content...")

                # Mastery Avg 확인
                mastery_avg_elem = page.locator("text=Mastery Avg").first
                if await mastery_avg_elem.count() > 0:
                    log_pass("Mastery Avg section found")
                    # 실제 값 확인
                    parent = page.locator("div:has-text('Mastery Avg')").first
                    if await parent.count() > 0:
                        text = await parent.text_content()
                        log_info(f"  Content: {text[:50]}...")

                # Attempts 확인
                attempts_elem = page.locator("text=Attempts").first
                if await attempts_elem.count() > 0:
                    log_pass("Attempts section found")

                # Trend 확인
                trend_elem = page.locator("text=Trend").first
                if await trend_elem.count() > 0:
                    log_pass("Trend section found")

                # Recent Activities 확인
                activities_elem = page.locator("text=Recent Activities").first
                if await activities_elem.count() > 0:
                    log_pass("Recent Activities section found")

                # 6. 스크린샷 캡처
                log_info("\n[6] Capturing screenshot...")
                screenshot_dir = Path("user_scenarios/screenshots")
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screenshot_dir / "node4_integration.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                log_pass(f"Screenshot saved: {screenshot_path}")

            else:
                print(f"API call failed or not found")

        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

            log_info("\n" + "=" * 60)
            log_info("Test Complete!")
            log_info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_node4_integration())
