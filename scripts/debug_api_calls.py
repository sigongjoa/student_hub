"""
Debug API Calls and Console Errors
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def debug_api():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Capture console messages
        console_messages = []
        def handle_console(msg):
            console_messages.append(f"[{msg.type}] {msg.text}")
            print(f"Console [{msg.type}]: {msg.text}")

        page.on("console", handle_console)

        # Capture API requests and responses
        api_calls = []
        async def handle_response(response):
            if "/api/" in response.url:
                status = response.status
                url = response.url
                print(f"\nAPI Call: {url}")
                print(f"Status: {status}")

                try:
                    body = await response.json()
                    print(f"Response: {json.dumps(body, indent=2, ensure_ascii=False)[:500]}")
                    api_calls.append({
                        "url": url,
                        "status": status,
                        "response": body
                    })
                except:
                    text = await response.text()
                    print(f"Response (text): {text[:200]}")
                    api_calls.append({
                        "url": url,
                        "status": status,
                        "response": text
                    })

        page.on("response", handle_response)

        try:
            # Navigate to students list
            print("=" * 60)
            print("Loading students list...")
            print("=" * 60)
            await page.goto("http://localhost:5173/students", wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            # Click first student
            print("\n" + "=" * 60)
            print("Clicking first student...")
            print("=" * 60)
            first_link = page.locator("tbody tr a").first
            await first_link.click()
            await page.wait_for_url("**/students/**", timeout=5000)
            print(f"Navigated to: {page.url}")

            # Wait for API calls
            print("\nWaiting for API calls...")
            await page.wait_for_timeout(5000)

            # Check page content
            print("\n" + "=" * 60)
            print("Page Content Check")
            print("=" * 60)

            # Check for "Loading..." text
            is_loading = await page.locator("text=Loading...").count()
            print(f"Loading indicator: {is_loading > 0}")

            # Check for "Student not found" text
            not_found = await page.locator("text=Student not found").count()
            print(f"Not found message: {not_found > 0}")

            # Check for student name in any element
            student_name_elem = await page.locator("text=/테스트 학생/").count()
            print(f"Student name found in page: {student_name_elem > 0}")

            # Take screenshot
            screenshot_dir = Path("user_scenarios/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / "api_debug.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\nScreenshot: {screenshot_path}")

            # Summary
            print("\n" + "=" * 60)
            print("Summary")
            print("=" * 60)
            print(f"Total API calls captured: {len(api_calls)}")
            for i, call in enumerate(api_calls):
                print(f"{i+1}. {call['url']} - Status: {call['status']}")

            print(f"\nTotal console messages: {len(console_messages)}")
            for msg in console_messages[:10]:  # First 10 messages
                print(f"  {msg}")

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_api())
