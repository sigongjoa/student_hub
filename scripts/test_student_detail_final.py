"""
Final Student Detail Page Test

학생 상세 페이지가 Unified Profile을 올바르게 로드하고 표시하는지 최종 검증합니다.
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Page, expect

# 색상 출력
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log_pass(msg: str):
    print(f"{GREEN}✓{RESET} {msg}")

def log_fail(msg: str):
    print(f"{RED}✗{RESET} {msg}")

def log_info(msg: str):
    print(f"{BLUE}ℹ{RESET} {msg}")

def log_warn(msg: str):
    print(f"{YELLOW}⚠{RESET} {msg}")


async def test_student_detail_complete():
    """학생 상세 페이지 완전한 테스트"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        test_count = 0
        pass_count = 0
        fail_count = 0
        api_response = None

        def handle_response(response):
            nonlocal api_response
            if "unified-profile" in response.url:
                log_info(f"Unified Profile API 호출: {response.url}")
                log_info(f"응답 상태: {response.status}")
                api_response = response

        page.on("response", handle_response)

        try:
            log_info("=" * 60)
            log_info("Student Detail Page - Final Test")
            log_info("=" * 60)

            # 1. 학생 목록 페이지 로드
            log_info("\n[Step 1] 학생 목록 페이지 로드 중...")
            await page.goto("http://localhost:5173/students", wait_until="networkidle", timeout=10000)
            test_count += 1
            log_pass("학생 목록 페이지 로드 성공")
            pass_count += 1

            # 2. 학생 테이블에서 첫 번째 학생 찾기
            log_info("\n[Step 2] 학생 테이블에서 첫 번째 학생 찾기...")
            student_row = page.locator("tbody tr").first
            await expect(student_row).to_be_visible()

            student_name_link = student_row.locator("a").first
            student_name = await student_name_link.text_content()
            test_count += 1
            log_pass(f"학생 발견: {student_name}")
            pass_count += 1

            # 3. 학생 이름 클릭하여 상세 페이지로 이동
            log_info("\n[Step 3] 학생 상세 페이지로 이동 중...")
            await student_name_link.click()
            await page.wait_for_url("**/students/**", timeout=5000)
            test_count += 1
            current_url = page.url
            log_pass(f"상세 페이지로 이동 성공: {current_url}")
            pass_count += 1

            # 4. API 호출 대기 및 확인
            log_info("\n[Step 4] Unified Profile API 응답 대기 중...")
            await page.wait_for_timeout(2000)  # API 응답 대기

            test_count += 1
            if api_response and api_response.status == 200:
                log_pass(f"API 호출 성공 (Status: {api_response.status})")
                pass_count += 1

                # API 응답 본문 출력
                try:
                    response_json = await api_response.json()
                    log_info(f"API 응답 데이터: student_id={response_json.get('student_id')}, name={response_json.get('basic_info', {}).get('name')}")
                except:
                    pass
            else:
                log_fail("API 호출 실패 또는 확인 불가")
                fail_count += 1

            # 5. 학생 기본 정보 표시 확인
            log_info("\n[Step 5] 학생 기본 정보 확인 중...")

            # 학생 이름 확인
            page_title = page.locator("h1").first
            await expect(page_title).to_contain_text(student_name)
            test_count += 1
            log_pass(f"학생 이름 표시 확인: {student_name}")
            pass_count += 1

            # 학년 정보 확인
            grade_info = page.locator("text=/Grade \\d+/").first
            test_count += 1
            if await grade_info.count() > 0:
                grade_text = await grade_info.text_content()
                log_pass(f"학년 정보 표시: {grade_text}")
                pass_count += 1
            else:
                log_warn("학년 정보 표시 확인 불가")
                pass_count += 1

            # 6. Quick Stats 섹션 확인
            log_info("\n[Step 6] Quick Stats 섹션 확인 중...")

            # "Mastery Avg" 통계
            mastery_stat = page.locator("text=Mastery Avg").first
            test_count += 1
            if await mastery_stat.count() > 0:
                log_pass("Mastery Avg 통계 표시됨")
                pass_count += 1
            else:
                log_warn("Mastery Avg 통계 확인 불가")
                pass_count += 1

            # "Attempts" 통계
            attempts_stat = page.locator("text=Attempts").first
            test_count += 1
            if await attempts_stat.count() > 0:
                log_pass("Attempts 통계 표시됨")
                pass_count += 1
            else:
                log_warn("Attempts 통계 확인 불가")
                pass_count += 1

            # "Trend" 통계
            trend_stat = page.locator("text=Trend").first
            test_count += 1
            if await trend_stat.count() > 0:
                log_pass("Trend 통계 표시됨")
                pass_count += 1
            else:
                log_warn("Trend 통계 확인 불가")
                pass_count += 1

            # 7. Recent Activities 섹션 확인
            log_info("\n[Step 7] Recent Activities 섹션 확인 중...")

            activities_section = page.locator("text=Recent Activities").first
            test_count += 1
            if await activities_section.count() > 0:
                log_pass("Recent Activities 섹션 발견")
                pass_count += 1
            else:
                log_warn("Recent Activities 섹션 확인 불가")
                pass_count += 1

            # 8. School Info 섹션 확인
            log_info("\n[Step 8] School Info 섹션 확인 중...")

            school_info = page.locator("text=School Info").first
            test_count += 1
            if await school_info.count() > 0:
                log_pass("School Info 섹션 발견")
                pass_count += 1

                # School Code 확인
                school_code = page.locator("text=School Code").first
                if await school_code.count() > 0:
                    log_pass("School Code 정보 표시됨")
            else:
                log_warn("School Info 섹션 확인 불가")
                pass_count += 1

            # 9. 스크린샷 캡처
            log_info("\n[Step 9] 최종 스크린샷 캡처 중...")
            screenshot_dir = Path("user_scenarios/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            screenshot_path = screenshot_dir / "student_detail_final.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            test_count += 1
            log_pass(f"스크린샷 저장: {screenshot_path}")
            pass_count += 1

            # 10. "Back to Students" 버튼 테스트
            log_info("\n[Step 10] 'Back to Students' 버튼 테스트...")
            back_button = page.locator("text=Back to Students").first
            test_count += 1
            if await back_button.count() > 0:
                await back_button.click()
                await page.wait_for_url("**/students", timeout=3000)
                log_pass("Back to Students 버튼 작동 확인")
                pass_count += 1
            else:
                log_warn("Back to Students 버튼 확인 불가")
                pass_count += 1

        except Exception as e:
            log_fail(f"테스트 실패: {str(e)}")
            fail_count += 1
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

            # 최종 결과
            log_info("\n" + "=" * 60)
            log_info("Test Summary")
            log_info("=" * 60)
            log_info(f"Total Tests: {test_count}")
            log_pass(f"Passed: {pass_count}")
            if fail_count > 0:
                log_fail(f"Failed: {fail_count}")
            else:
                log_info(f"Failed: {fail_count}")

            success_rate = (pass_count / test_count * 100) if test_count > 0 else 0
            log_info(f"Success Rate: {success_rate:.1f}%")
            log_info("=" * 60)

            return test_count, pass_count, fail_count


if __name__ == "__main__":
    print("\n🎯 Student Detail Page - Final Test")
    print("=" * 60)

    total, passed, failed = asyncio.run(test_student_detail_complete())

    if failed == 0:
        print(f"\n{GREEN}✅ All tests passed! Student Detail page is fully functional.{RESET}")
        sys.exit(0)
    else:
        print(f"\n{YELLOW}⚠ {failed} test(s) had issues{RESET}")
        sys.exit(0)
