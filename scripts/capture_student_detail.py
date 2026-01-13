"""
Capture Student Detail Page Screenshot
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture_detail_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Navigate to students list
            print("Loading students list...")
            await page.goto("http://localhost:5173/students", wait_until="networkidle")

            # Click first student
            print("Clicking first student...")
            first_link = page.locator("tbody tr a").first
            student_name = await first_link.text_content()
            print(f"Student name: {student_name}")

            await first_link.click()
            await page.wait_for_url("**/students/**")
            print(f"Navigated to: {page.url}")

            # Wait for content
            await page.wait_for_timeout(3000)

            # Capture screenshot
            screenshot_dir = Path("user_scenarios/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / "student_detail_debug.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

            # Print all h1 elements
            print("\nAll H1 elements:")
            h1_elements = await page.locator("h1").all()
            for i, h1 in enumerate(h1_elements):
                text = await h1.text_content()
                print(f"{i+1}. H1: '{text}'")

            # Print all h2 elements
            print("\nAll H2 elements:")
            h2_elements = await page.locator("h2").all()
            for i, h2 in enumerate(h2_elements):
                text = await h2.text_content()
                print(f"{i+1}. H2: '{text}'")

            # Print page HTML structure (first 3000 chars)
            print("\nPage HTML:")
            html = await page.content()
            print(html[:3000])

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_detail_page())
