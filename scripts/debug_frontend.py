"""
Debug Frontend Structure

학생 목록 페이지의 HTML 구조를 파악합니다.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def debug_students_page():
    """학생 목록 페이지 디버깅"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("Loading students page...")
            await page.goto("http://localhost:5173/students", wait_until="networkidle", timeout=15000)
            print("Page loaded!")

            # 스크린샷 캡처
            screenshot_dir = Path("user_scenarios/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / "debug_students_page.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

            # HTML 구조 출력
            html_content = await page.content()
            print("\n=== Page HTML Structure ===")
            print(html_content[:2000])  # 첫 2000자

            # 모든 링크 찾기
            print("\n=== All Links ===")
            links = await page.locator("a").all()
            for i, link in enumerate(links[:10]):  # 처음 10개만
                text = await link.text_content()
                href = await link.get_attribute("href")
                print(f"{i+1}. Text: '{text}', Href: '{href}'")

            # "student" 키워드가 포함된 요소 찾기
            print("\n=== Elements containing 'student' ===")
            student_elems = await page.locator("*:has-text('student')").all()
            print(f"Found {len(student_elems)} elements with 'student' text")

            # data-testid 속성을 가진 모든 요소
            print("\n=== Elements with data-testid ===")
            testid_elems = await page.locator("[data-testid]").all()
            for elem in testid_elems[:10]:
                testid = await elem.get_attribute("data-testid")
                print(f"- data-testid='{testid}'")

            print("\nPage title:", await page.title())
            print("Page URL:", page.url)

            # 5초 대기 (수동 확인용)
            print("\nWaiting 5 seconds for manual inspection...")
            await page.wait_for_timeout(5000)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_students_page())
