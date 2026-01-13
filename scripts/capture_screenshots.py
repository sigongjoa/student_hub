"""
Playwright 스크린샷 자동 생성 스크립트

모든 Phase 0 기능의 스크린샷을 촬영하여 user_manual/screenshots/에 저장
"""
import asyncio
import subprocess
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# 스크린샷 저장 디렉토리
SCREENSHOT_DIR = Path("user_manual/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://localhost:8000"


def wait_for_server(max_retries=30):
    """서버가 시작될 때까지 대기"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                print("✅ 서버 시작 완료")
                return True
        except:
            print(f"⏳ 서버 대기 중... ({i+1}/{max_retries})")
            time.sleep(1)
    return False


def setup_test_data():
    """테스트 데이터 생성"""
    print("\n📊 테스트 데이터 생성 중...")

    # Use Case 2: 이차방정식 학습 (2 정답, 1 오답)
    attempts_quadratic = [
        {"student_id": "screenshot_student", "question_id": "q_001", "concept": "이차방정식", "is_correct": True, "response_time_ms": 45000},
        {"student_id": "screenshot_student", "question_id": "q_002", "concept": "이차방정식", "is_correct": True, "response_time_ms": 30000},
        {"student_id": "screenshot_student", "question_id": "q_003", "concept": "이차방정식", "is_correct": False, "response_time_ms": 120000},
    ]

    # Use Case 3: 프로파일 - 여러 개념
    attempts_profile = [
        # 미분: 4 정답, 1 오답 (강점)
        {"student_id": "screenshot_student", "question_id": "q_101", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_102", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_103", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_104", "concept": "미분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_105", "concept": "미분", "is_correct": False},
        # 적분: 1 정답, 3 오답 (약점)
        {"student_id": "screenshot_student", "question_id": "q_201", "concept": "적분", "is_correct": True},
        {"student_id": "screenshot_student", "question_id": "q_202", "concept": "적분", "is_correct": False},
        {"student_id": "screenshot_student", "question_id": "q_203", "concept": "적분", "is_correct": False},
        {"student_id": "screenshot_student", "question_id": "q_204", "concept": "적분", "is_correct": False},
    ]

    all_attempts = attempts_quadratic + attempts_profile

    for attempt in all_attempts:
        try:
            response = requests.post(f"{BASE_URL}/api/attempts", json=attempt, timeout=5)
            if response.status_code != 201:
                print(f"⚠️  시도 기록 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 에러: {e}")

    print(f"✅ {len(all_attempts)}개 시도 기록 생성 완료")


def capture_screenshots():
    """모든 페이지 스크린샷 촬영"""
    print("\n📸 스크린샷 촬영 시작...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless 모드로 실행
        page = browser.new_page(viewport={"width": 1200, "height": 900})

        # 1. 홈 페이지
        print("  📷 홈 페이지...")
        page.goto(BASE_URL)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_DIR / "home_page.png"))

        # 2. 숙련도 페이지 (이차방정식)
        print("  📷 숙련도 페이지...")
        page.goto(f"{BASE_URL}/mastery/screenshot_student/이차방정식")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_DIR / "mastery_page_example.png"))

        # 3. 프로파일 페이지
        print("  📷 프로파일 페이지...")
        page.goto(f"{BASE_URL}/profile/screenshot_student")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_DIR / "profile_page_example.png"))

        # 4. 약점 개념 페이지
        print("  📷 약점 개념 페이지...")
        page.goto(f"{BASE_URL}/weak-concepts/screenshot_student")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_DIR / "weak_concepts_page_example.png"))

        # 5. API 문서 (Swagger)
        print("  📷 API 문서...")
        page.goto(f"{BASE_URL}/docs")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_DIR / "api_docs.png"))

        browser.close()

    print("✅ 스크린샷 촬영 완료")


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("Playwright 스크린샷 자동 생성")
    print("=" * 70)

    # 1. 서버 시작
    print("\n🚀 FastAPI 서버 시작 중...")
    server_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "app.api_app:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # 2. 서버 대기
        if not wait_for_server():
            print("❌ 서버 시작 실패")
            return

        # 3. 테스트 데이터 생성
        setup_test_data()

        # 4. 스크린샷 촬영
        capture_screenshots()

        # 5. 결과 확인
        print("\n" + "=" * 70)
        print("✅ 모든 스크린샷 생성 완료!")
        print("=" * 70)
        print(f"\n저장 위치: {SCREENSHOT_DIR.absolute()}")
        print("\n생성된 파일:")
        for screenshot in sorted(SCREENSHOT_DIR.glob("*.png")):
            print(f"  - {screenshot.name}")

    finally:
        # 6. 서버 종료
        print("\n🛑 서버 종료 중...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ 서버 종료 완료")


if __name__ == "__main__":
    main()
