"""
스크린샷 캡처 테스트

USER_MANUAL.md에 사용할 스크린샷을 자동으로 생성
"""
import pytest
from playwright.sync_api import Page
import requests
from pathlib import Path


# 스크린샷 저장 경로
SCREENSHOT_DIR = Path("user_manual/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.mark.e2e
def test_capture_all_screenshots(page: Page, api_base_url: str):
    """
    모든 Phase 0 기능의 스크린샷을 촬영

    생성되는 스크린샷:
    1. home_page.png - 홈 페이지
    2. mastery_page_example.png - 숙련도 페이지
    3. profile_page_example.png - 프로파일 페이지
    4. weak_concepts_page_example.png - 약점 개념 페이지
    5. api_docs.png - API 문서
    """

    # === 테스트 데이터 생성 ===

    # Use Case 2: 이차방정식 (2 정답, 1 오답 = 49.3%)
    quadratic_attempts = [
        {"student_id": "screenshot_student", "question_id": "q_001", "concept": "이차방정식", "is_correct": True, "response_time_ms": 45000},
        {"student_id": "screenshot_student", "question_id": "q_002", "concept": "이차방정식", "is_correct": True, "response_time_ms": 30000},
        {"student_id": "screenshot_student", "question_id": "q_003", "concept": "이차방정식", "is_correct": False, "response_time_ms": 120000},
    ]

    # Use Case 3: 프로파일 - 여러 개념
    profile_attempts = [
        # 미분: 4 정답, 1 오답 (81.2% - 강점)
        {"student_id": "screenshot_student", "question_id": "q_101", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_102", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_103", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_104", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_105", "concept": "미분", "is_correct": False},
        # 적분: 1 정답, 3 오답 (35.6% - 약점)
        {"student_id": "screenshot_student", "question_id": "q_201", "concept": "적분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_202", "concept": "적분", "is_correct": False},
        {"student_id": "screenshot_student", "question_id": "q_203", "concept": "적분", "is_correct": False},
        {"student_id": "screenshot_student", "question_id": "q_204", "concept": "적분", "is_correct": False},
    ]

    all_attempts = quadratic_attempts + profile_attempts

    for attempt in all_attempts:
        response = requests.post(f"{api_base_url}/api/attempts", json=attempt)
        assert response.status_code == 201, f"Failed to create attempt: {response.status_code}"

    print(f"\n✅ {len(all_attempts)}개 시도 기록 생성 완료")

    # === 스크린샷 촬영 ===

    # 1. 홈 페이지
    print("📷 홈 페이지 스크린샷 촬영...")
    page.goto(api_base_url)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(SCREENSHOT_DIR / "home_page.png"))

    # 2. 숙련도 페이지 (이차방정식)
    print("📷 숙련도 페이지 스크린샷 촬영...")
    page.goto(f"{api_base_url}/mastery/screenshot_student/이차방정식")
    page.wait_for_timeout(1000)

    # 숙련도 값이 표시될 때까지 대기
    page.wait_for_selector("[data-testid='mastery-value']", timeout=10000)
    page.screenshot(path=str(SCREENSHOT_DIR / "mastery_page_example.png"))

    # 3. 프로파일 페이지
    print("📷 프로파일 페이지 스크린샷 촬영...")
    page.goto(f"{api_base_url}/profile/screenshot_student")
    page.wait_for_timeout(1000)

    # 개념 카드들이 표시될 때까지 대기
    page.wait_for_selector("[data-testid='concept-card']", timeout=10000)
    page.screenshot(path=str(SCREENSHOT_DIR / "profile_page_example.png"))

    # 4. 약점 개념 페이지
    print("📷 약점 개념 페이지 스크린샷 촬영...")
    page.goto(f"{api_base_url}/weak-concepts/screenshot_student")
    page.wait_for_timeout(1000)

    # 약점 배지가 표시될 때까지 대기
    page.wait_for_selector("[data-testid='weak-concept-badge']", timeout=10000)
    page.screenshot(path=str(SCREENSHOT_DIR / "weak_concepts_page_example.png"))

    # 5. API 문서
    print("📷 API 문서 스크린샷 촬영...")
    page.goto(f"{api_base_url}/docs")
    page.wait_for_timeout(2000)
    page.screenshot(path=str(SCREENSHOT_DIR / "api_docs.png"))

    # === 결과 확인 ===

    print("\n" + "=" * 70)
    print("✅ 모든 스크린샷 생성 완료!")
    print("=" * 70)
    print(f"\n저장 위치: {SCREENSHOT_DIR.absolute()}")
    print("\n생성된 파일:")
    for screenshot in sorted(SCREENSHOT_DIR.glob("*.png")):
        print(f"  - {screenshot.name}")

    # 스크린샷 파일이 실제로 생성되었는지 확인
    assert (SCREENSHOT_DIR / "home_page.png").exists()
    assert (SCREENSHOT_DIR / "mastery_page_example.png").exists()
    assert (SCREENSHOT_DIR / "profile_page_example.png").exists()
    assert (SCREENSHOT_DIR / "weak_concepts_page_example.png").exists()
    assert (SCREENSHOT_DIR / "api_docs.png").exists()
