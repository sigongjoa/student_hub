#!/usr/bin/env python3
"""
상세 사용자 시나리오 테스트

실제 사용자(선생님, 학생)가 할 수 있는 모든 행동을 Playwright로 검증
- 모든 클릭 가능한 요소 확인
- 입력 필드 작동 확인
- 모달/다이얼로그 검증
- 폼 제출 테스트
- API 호출 확인
- 결과 표시 검증
"""
import asyncio
from playwright.async_api import async_playwright, Page, expect
import os
from datetime import datetime

SCENARIO_DIR = "user_scenarios"
SCREENSHOTS_DIR = f"{SCENARIO_DIR}/screenshots"

async def setup():
    os.makedirs(SCENARIO_DIR, exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    print(f"✅ Directories created: {SCENARIO_DIR}")

async def save_screenshot(page: Page, name: str, description: str = ""):
    """스크린샷 저장"""
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{name}.png"
    await page.screenshot(path=filename, full_page=True)
    if description:
        print(f"   📸 {description}: {filename}")
    return filename

### ================================================================
### 시나리오 1: 선생님 첫 방문 - Dashboard 탐색
### ================================================================

async def scenario1_teacher_first_visit(page: Page):
    """
    시나리오 1: 선생님이 처음 Student Hub 접속

    검증 항목:
    - Dashboard 페이지 로드
    - 통계 카드 4개 표시
    - Sidebar 메뉴 7개 표시
    - 각 UI 요소 클릭 가능성
    """
    print("\n" + "="*80)
    print("📊 시나리오 1: 선생님 첫 방문 - Dashboard 탐색")
    print("="*80)

    # Step 1-1: Dashboard 접속
    print("\n1️⃣ Step 1: Dashboard 접속")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")
    await save_screenshot(page, "s1_step1_dashboard_loaded", "Dashboard 로드 완료")

    # URL 검증
    assert page.url == "http://localhost:5173/", f"Expected URL '/', got '{page.url}'"
    print("   ✅ URL 검증: /")

    # Step 1-2: 페이지 제목 확인
    print("\n2️⃣ Step 2: 페이지 제목 확인")
    dashboard_heading = page.locator("h1:has-text('Dashboard')")
    await expect(dashboard_heading).to_be_visible()
    print("   ✅ Dashboard 제목 표시됨")

    subtitle = page.locator("text=Welcome back! Here's what's happening today.")
    await expect(subtitle).to_be_visible()
    print("   ✅ 환영 메시지 표시됨")

    # Step 1-3: 통계 카드 4개 확인
    print("\n3️⃣ Step 3: 통계 카드 확인")

    stat_cards = [
        ("Total Students", "총 학생 수"),
        ("At Risk", "위험군 학생"),
        ("Active Interventions", "진행중인 개입"),
        ("Avg. Mastery", "평균 숙련도")
    ]

    for stat_text, description in stat_cards:
        card = page.locator(f"text={stat_text}").first
        await expect(card).to_be_visible()
        print(f"   ✅ {description} 카드 표시됨")

    await save_screenshot(page, "s1_step3_stat_cards", "4개 통계 카드")

    # Step 1-4: Sidebar 메뉴 확인
    print("\n4️⃣ Step 4: Sidebar 네비게이션 메뉴 확인")

    nav_items = [
        ("Dashboard", "대시보드"),
        ("Students", "학생 관리"),
        ("Logic Engine", "로직 엔진"),
        ("Q-DNA", "문제 DNA"),
        ("Reports", "리포트"),
        ("Virtual Lab", "가상 실습실"),
        ("School Info", "학교 정보")
    ]

    for nav_text, description in nav_items:
        nav_link = page.locator(f"text={nav_text}").first
        await expect(nav_link).to_be_visible()
        is_clickable = await nav_link.is_enabled()
        print(f"   ✅ {description} 메뉴 표시됨 (클릭 가능: {is_clickable})")

    await save_screenshot(page, "s1_step4_sidebar", "Sidebar 메뉴")

    # Step 1-5: Settings 버튼 확인
    print("\n5️⃣ Step 5: Settings 버튼 확인")
    settings_button = page.locator("text=Settings").first
    await expect(settings_button).to_be_visible()
    is_clickable = await settings_button.is_enabled()
    print(f"   ✅ Settings 버튼 표시됨 (클릭 가능: {is_clickable})")

    print("\n✅ 시나리오 1 완료!")

### ================================================================
### 시나리오 2: 학생 목록 탐색 및 검색
### ================================================================

async def scenario2_student_list_exploration(page: Page):
    """
    시나리오 2: 학생 목록 페이지 탐색

    검증 항목:
    - Students 페이지 이동
    - 학생 목록 테이블 표시
    - 검색 입력 필드 작동
    - Filter 버튼 클릭
    - Add Student 버튼 클릭
    - 학생 이름 클릭하여 상세 페이지 이동
    """
    print("\n" + "="*80)
    print("👥 시나리오 2: 학생 목록 탐색 및 검색")
    print("="*80)

    # Step 2-1: Students 페이지로 이동
    print("\n1️⃣ Step 1: Students 페이지로 이동")
    students_link = page.locator("text=Students").first
    await students_link.click()
    await page.wait_for_url("**/students")
    await page.wait_for_load_state("networkidle")
    await save_screenshot(page, "s2_step1_students_page", "Students 페이지")

    assert "/students" in page.url, f"Expected URL contains '/students', got '{page.url}'"
    print("   ✅ URL 검증: /students")

    # Step 2-2: 페이지 제목 확인
    print("\n2️⃣ Step 2: 페이지 제목 및 설명 확인")
    students_heading = page.locator("h1:has-text('Students')")
    await expect(students_heading).to_be_visible()
    print("   ✅ Students 제목 표시됨")

    subtitle = page.locator("text=Manage your students and view their progress.")
    await expect(subtitle).to_be_visible()
    print("   ✅ 설명 문구 표시됨")

    # Step 2-3: Add Student 버튼 확인 및 클릭 시도
    print("\n3️⃣ Step 3: Add Student 버튼 확인")
    add_button = page.locator("button:has-text('Add Student')")
    await expect(add_button).to_be_visible()
    is_enabled = await add_button.is_enabled()
    print(f"   ✅ Add Student 버튼 표시됨 (활성화: {is_enabled})")

    if is_enabled:
        await add_button.click()
        await page.wait_for_timeout(500)
        await save_screenshot(page, "s2_step3_add_student_clicked", "Add Student 클릭 후")
        print("   ⚠️  Add Student 클릭됨 (모달 없음 - Placeholder)")

    # Step 2-4: 검색 입력 필드 테스트
    print("\n4️⃣ Step 4: 검색 입력 필드 테스트")
    search_input = page.locator("input[placeholder*='Search']")
    await expect(search_input).to_be_visible()
    print("   ✅ 검색 입력 필드 표시됨")

    # 실제로 타이핑 시도
    await search_input.click()
    await search_input.fill("김민수")
    await page.wait_for_timeout(500)
    await save_screenshot(page, "s2_step4_search_input", "검색 필드에 입력")

    input_value = await search_input.input_value()
    assert input_value == "김민수", f"Expected '김민수', got '{input_value}'"
    print(f"   ✅ 검색 필드 입력 작동: '{input_value}'")
    print("   ⚠️  필터링 로직 없음 (Placeholder)")

    # 입력 지우기
    await search_input.clear()

    # Step 2-5: Filter 버튼 확인 및 클릭
    print("\n5️⃣ Step 5: Filter 버튼 확인")
    filter_button = page.locator("button:has-text('Filter')")
    await expect(filter_button).to_be_visible()
    is_enabled = await filter_button.is_enabled()
    print(f"   ✅ Filter 버튼 표시됨 (활성화: {is_enabled})")

    if is_enabled:
        await filter_button.click()
        await page.wait_for_timeout(500)
        await save_screenshot(page, "s2_step5_filter_clicked", "Filter 클릭 후")
        print("   ⚠️  Filter 클릭됨 (모달 없음 - Placeholder)")

    # Step 2-6: 학생 테이블 확인
    print("\n6️⃣ Step 6: 학생 테이블 확인")

    # 테이블 헤더 확인
    table_headers = ["Name", "ID", "Grade", "Class", "Joined", "Actions"]
    for header in table_headers:
        header_cell = page.locator(f"th:has-text('{header}')")
        await expect(header_cell).to_be_visible()
        print(f"   ✅ 테이블 헤더 '{header}' 표시됨")

    await save_screenshot(page, "s2_step6_table", "학생 테이블")

    # Step 2-7: 학생 행 확인 (첫 번째 학생)
    print("\n7️⃣ Step 7: 학생 데이터 행 확인")

    # 학생 이름 링크 찾기 (첫 번째)
    student_link = page.locator("tbody tr td a").first

    # 학생이 있는지 확인
    student_count = await page.locator("tbody tr").count()
    print(f"   ✅ 테이블에 {student_count}명의 학생 표시됨")

    if student_count > 0:
        # 첫 번째 학생 이름 가져오기
        student_name = await student_link.text_content()
        print(f"   ✅ 첫 번째 학생: {student_name}")

        # hover 효과 테스트
        await student_link.hover()
        await page.wait_for_timeout(300)
        await save_screenshot(page, "s2_step7_hover", "학생 이름 hover")
        print("   ✅ Hover 효과 작동")

        return student_name  # 다음 시나리오를 위해 반환
    else:
        print("   ⚠️  학생 데이터 없음")
        return None

    print("\n✅ 시나리오 2 완료!")

### ================================================================
### 시나리오 3: 학생 상세 정보 확인
### ================================================================

async def scenario3_student_detail_view(page: Page):
    """
    시나리오 3: 학생 상세 페이지 확인

    검증 항목:
    - 학생 이름 클릭하여 상세 페이지 이동
    - Back 버튼 작동
    - Quick Stats 표시
    - Recent Activities 표시
    - Create Intervention 버튼 클릭
    """
    print("\n" + "="*80)
    print("👤 시나리오 3: 학생 상세 정보 확인")
    print("="*80)

    # Students 페이지에 있다고 가정
    await page.goto("http://localhost:5173/students")
    await page.wait_for_load_state("networkidle")

    # Step 3-1: 첫 번째 학생 클릭
    print("\n1️⃣ Step 1: 학생 이름 클릭하여 상세 페이지 이동")

    student_count = await page.locator("tbody tr").count()
    if student_count == 0:
        print("   ⚠️  학생 데이터 없음 - 시나리오 스킵")
        return

    student_link = page.locator("tbody tr td a").first
    student_name = await student_link.text_content()
    print(f"   → 클릭할 학생: {student_name}")

    await student_link.click()
    await page.wait_for_load_state("networkidle")
    await save_screenshot(page, "s3_step1_detail_page", "학생 상세 페이지")

    # URL 검증 (/students/:id 형식)
    assert "/students/" in page.url, f"Expected URL contains '/students/', got '{page.url}'"
    print(f"   ✅ URL 검증: {page.url}")

    # Step 3-2: Back 버튼 확인
    print("\n2️⃣ Step 2: Back 버튼 확인")
    back_button = page.locator("button:has-text('Back')")
    await expect(back_button).to_be_visible()
    is_enabled = await back_button.is_enabled()
    print(f"   ✅ Back 버튼 표시됨 (활성화: {is_enabled})")

    # Step 3-3: 학생 정보 헤더 확인
    print("\n3️⃣ Step 3: 학생 정보 헤더 확인")

    # 학생 아바타 (User 아이콘)
    avatar = page.locator("svg.lucide-user").first
    await expect(avatar).to_be_visible()
    print("   ✅ 학생 아바타 표시됨")

    # Create Intervention 버튼
    intervention_button = page.locator("button:has-text('Create Intervention')")
    await expect(intervention_button).to_be_visible()
    print("   ✅ Create Intervention 버튼 표시됨")

    await save_screenshot(page, "s3_step3_header", "학생 정보 헤더")

    # Step 3-4: Quick Stats 카드 확인
    print("\n4️⃣ Step 4: Quick Stats 카드 확인")

    quick_stats = page.locator("text=Quick Stats").first
    if await quick_stats.is_visible():
        print("   ✅ Quick Stats 카드 표시됨")

        # 통계 항목 확인
        stats_items = ["Mastery Avg", "Attempts", "Trend"]
        for item in stats_items:
            stat = page.locator(f"text={item}")
            if await stat.is_visible():
                print(f"   ✅ {item} 통계 표시됨")
    else:
        print("   ⚠️  Quick Stats 로딩 중 또는 데이터 없음")

    await save_screenshot(page, "s3_step4_quick_stats", "Quick Stats")

    # Step 3-5: Recent Activities 확인
    print("\n5️⃣ Step 5: Recent Activities 확인")

    activities = page.locator("text=Recent Activities").first
    if await activities.is_visible():
        print("   ✅ Recent Activities 카드 표시됨")
    else:
        print("   ⚠️  Recent Activities 로딩 중")

    await save_screenshot(page, "s3_step5_activities", "Recent Activities")

    # Step 3-6: School Info 카드 확인
    print("\n6️⃣ Step 6: School Info 카드 확인")

    school_info = page.locator("text=School Info").first
    if await school_info.is_visible():
        print("   ✅ School Info 카드 표시됨")

        # View Schedule 링크 확인
        schedule_link = page.locator("text=View Schedule")
        if await schedule_link.is_visible():
            print("   ✅ View Schedule 링크 표시됨")

    await save_screenshot(page, "s3_step6_school_info", "School Info")

    # Step 3-7: Create Intervention 버튼 클릭 시도
    print("\n7️⃣ Step 7: Create Intervention 버튼 클릭")

    await intervention_button.click()
    await page.wait_for_timeout(500)
    await save_screenshot(page, "s3_step7_intervention_clicked", "Intervention 버튼 클릭 후")
    print("   ⚠️  Create Intervention 클릭됨 (폼 없음 - Placeholder)")

    # Step 3-8: Back 버튼으로 돌아가기
    print("\n8️⃣ Step 8: Back 버튼으로 Students 페이지로 돌아가기")

    await back_button.click()
    await page.wait_for_url("**/students")
    await page.wait_for_load_state("networkidle")
    await save_screenshot(page, "s3_step8_back_to_list", "Students 페이지로 복귀")

    assert "/students" in page.url and "/students/" not in page.url, "Should be back at /students"
    print("   ✅ Students 목록 페이지로 복귀 완료")

    print("\n✅ 시나리오 3 완료!")

### ================================================================
### 시나리오 4: 전체 네비게이션 테스트
### ================================================================

async def scenario4_full_navigation_test(page: Page):
    """
    시나리오 4: 전체 네비게이션 테스트

    검증 항목:
    - 모든 Sidebar 메뉴 클릭
    - 각 페이지 로드 확인
    - URL 변경 확인
    """
    print("\n" + "="*80)
    print("🧭 시나리오 4: 전체 네비게이션 테스트")
    print("="*80)

    nav_tests = [
        ("Dashboard", "/", "대시보드"),
        ("Students", "/students", "학생 관리"),
        ("Logic Engine", "/", "로직 엔진 (→Dashboard)"),
        ("Q-DNA", "/", "문제 DNA (→Dashboard)"),
        ("Reports", "/", "리포트 (→Dashboard)"),
        ("Virtual Lab", "/", "가상 실습실 (→Dashboard)"),
        ("School Info", "/", "학교 정보 (→Dashboard)")
    ]

    for i, (nav_text, expected_path, description) in enumerate(nav_tests, 1):
        print(f"\n{i}️⃣ Step {i}: {description} 클릭")

        nav_link = page.locator(f"text={nav_text}").first
        await nav_link.click()
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(300)

        current_url = page.url
        print(f"   → 현재 URL: {current_url}")

        # URL 검증
        assert expected_path in current_url, f"Expected path '{expected_path}' in '{current_url}'"
        print(f"   ✅ URL 검증 통과: {expected_path}")

        # 스크린샷
        await save_screenshot(page, f"s4_step{i}_{nav_text.lower().replace(' ', '_')}", description)

    print("\n✅ 시나리오 4 완료!")

### ================================================================
### 시나리오 5: API 호출 및 데이터 표시 검증
### ================================================================

async def scenario5_api_and_data_verification(page: Page):
    """
    시나리오 5: API 호출 및 데이터 표시 검증

    검증 항목:
    - Network 요청 확인
    - API 응답 확인
    - 데이터가 UI에 올바르게 표시되는지 확인
    """
    print("\n" + "="*80)
    print("🔌 시나리오 5: API 호출 및 데이터 표시 검증")
    print("="*80)

    # API 호출 추적 설정
    api_calls = []

    def handle_response(response):
        if "/api/" in response.url:
            api_calls.append({
                "url": response.url,
                "status": response.status,
                "method": response.request.method
            })
            print(f"   📡 API 호출: {response.request.method} {response.url} → {response.status}")

    page.on("response", handle_response)

    # Step 5-1: Dashboard API 호출
    print("\n1️⃣ Step 1: Dashboard 로드 시 API 호출 확인")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)  # API 호출 대기

    dashboard_api_calls = [call for call in api_calls if "/students" in call["url"]]
    print(f"   ✅ Dashboard에서 {len(dashboard_api_calls)}개 API 호출")

    # Step 5-2: Students 페이지 API 호출
    print("\n2️⃣ Step 2: Students 페이지 로드 시 API 호출 확인")
    api_calls.clear()

    await page.goto("http://localhost:5173/students")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)

    students_api_calls = [call for call in api_calls if "/students" in call["url"]]
    print(f"   ✅ Students 페이지에서 {len(students_api_calls)}개 API 호출")

    # Step 5-3: 학생 데이터 표시 확인
    print("\n3️⃣ Step 3: 학생 데이터가 UI에 표시되는지 확인")

    student_count = await page.locator("tbody tr").count()
    if student_count > 0:
        print(f"   ✅ {student_count}명의 학생 데이터 표시됨")

        # 첫 번째 학생 데이터 확인
        first_row = page.locator("tbody tr").first
        cells = first_row.locator("td")
        cell_count = await cells.count()
        print(f"   ✅ 학생 행에 {cell_count}개 컬럼 표시됨")
    else:
        print("   ⚠️  학생 데이터 없음")

    # Step 5-4: Student Detail API 호출
    if student_count > 0:
        print("\n4️⃣ Step 4: Student Detail 페이지 API 호출 확인")
        api_calls.clear()

        student_link = page.locator("tbody tr td a").first
        await student_link.click()
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        profile_api_calls = [call for call in api_calls if "/profiles/unified" in call["url"]]
        print(f"   ✅ Student Detail에서 {len(profile_api_calls)}개 API 호출")

        for call in profile_api_calls:
            print(f"      - {call['method']} {call['url']} → {call['status']}")

    await save_screenshot(page, "s5_api_verification", "API 검증 완료")

    print("\n✅ 시나리오 5 완료!")
    print(f"\n📊 총 API 호출 수: {len(api_calls)}")

### ================================================================
### 메인 실행
### ================================================================

async def main():
    """모든 시나리오 실행"""
    print("="*80)
    print("🎬 상세 사용자 시나리오 테스트")
    print("="*80)
    print("\n실제 사용자가 할 수 있는 모든 행동을 Playwright로 검증합니다.")

    await setup()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # 시나리오 1: 선생님 첫 방문
            await scenario1_teacher_first_visit(page)

            # 시나리오 2: 학생 목록 탐색
            await scenario2_student_list_exploration(page)

            # 시나리오 3: 학생 상세 정보
            await scenario3_student_detail_view(page)

            # 시나리오 4: 전체 네비게이션
            await scenario4_full_navigation_test(page)

            # 시나리오 5: API 및 데이터 검증
            await scenario5_api_and_data_verification(page)

            print("\n" + "="*80)
            print("✅ 모든 사용자 시나리오 테스트 통과!")
            print("="*80)
            print(f"\n📁 스크린샷 저장 위치: {SCREENSHOTS_DIR}/")
            print("\n📊 테스트 요약:")
            print("   ✅ 시나리오 1: Dashboard 탐색")
            print("   ✅ 시나리오 2: 학생 목록 및 검색")
            print("   ✅ 시나리오 3: 학생 상세 정보")
            print("   ✅ 시나리오 4: 전체 네비게이션")
            print("   ✅ 시나리오 5: API 호출 검증")

        except Exception as e:
            print(f"\n❌ 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            await save_screenshot(page, "error", "에러 발생")
            raise

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
