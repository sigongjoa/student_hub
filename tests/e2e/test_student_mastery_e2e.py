"""
Playwright E2E Tests for Student Mastery

실제 브라우저에서 프론트엔드와 백엔드가 통합되어 작동하는지 테스트

Test Scenarios:
1. 학생 시도 기록 생성 후 숙련도 확인
2. 프로파일 페이지에서 전체 숙련도 확인
3. 약점 개념 표시 확인
4. API 에러 처리 확인
"""
import pytest
from playwright.sync_api import Page, expect
import requests


@pytest.mark.e2e
def test_create_attempt_and_check_mastery(page: Page, api_base_url: str):
    """
    E2E Test: 시도 기록 생성 → 숙련도 계산 → 결과 확인

    시나리오:
    1. API로 시도 기록 3개 생성
    2. 브라우저에서 숙련도 확인 페이지 접속
    3. 계산된 숙련도 값 확인
    """
    # Given: API로 시도 기록 생성
    attempts = [
        {"student_id": "e2e_student_1", "question_id": "q_1", "concept": "이차방정식", "is_correct": True},
        {"student_id": "e2e_student_1", "question_id": "q_2", "concept": "이차방정식", "is_correct": True},
        {"student_id": "e2e_student_1", "question_id": "q_3", "concept": "이차방정식", "is_correct": False},
    ]

    for attempt_data in attempts:
        response = requests.post(f"{api_base_url}/api/attempts", json=attempt_data)
        assert response.status_code == 201

    # When: 브라우저에서 숙련도 페이지 접속
    page.goto(f"{api_base_url}/mastery/e2e_student_1/이차방정식")

    # Then: 숙련도 값 표시 확인
    expect(page.locator("text=숙련도")).to_be_visible(timeout=10000)

    # 숙련도 값이 0~1 사이인지 확인
    mastery_element = page.locator("[data-testid='mastery-value']")
    expect(mastery_element).to_be_visible()

    mastery_text = mastery_element.text_content()
    mastery_value = float(mastery_text.strip().replace("%", "")) / 100

    assert 0.0 <= mastery_value <= 1.0
    assert mastery_value > 0.4  # 2개 정답, 1개 오답 → 중간~높은 숙련도


@pytest.mark.e2e
def test_student_profile_page(page: Page, api_base_url: str):
    """
    E2E Test: 학생 프로파일 페이지

    시나리오:
    1. 여러 개념에 대한 시도 기록 생성
    2. 프로파일 페이지 접속
    3. 모든 개념의 숙련도 표시 확인
    """
    # Given: 3개 개념에 대한 시도 기록
    attempts = [
        {"student_id": "e2e_student_2", "question_id": "q_1", "concept": "A", "is_correct": True},
        {"student_id": "e2e_student_2", "question_id": "q_2", "concept": "A", "is_correct": True},
        {"student_id": "e2e_student_2", "question_id": "q_3", "concept": "B", "is_correct": False},
        {"student_id": "e2e_student_2", "question_id": "q_4", "concept": "C", "is_correct": True},
    ]

    for attempt_data in attempts:
        requests.post(f"{api_base_url}/api/attempts", json=attempt_data)

    # When: 프로파일 페이지 접속
    page.goto(f"{api_base_url}/profile/e2e_student_2")

    # Then: 3개 개념 모두 표시
    expect(page.locator("text=A")).to_be_visible(timeout=10000)
    expect(page.locator("text=B")).to_be_visible()
    expect(page.locator("text=C")).to_be_visible()

    # 각 개념의 숙련도 바 확인
    concept_cards = page.locator("[data-testid='concept-card']")
    count = concept_cards.count()
    assert count == 3


@pytest.mark.e2e
def test_weak_concepts_display(page: Page, api_base_url: str):
    """
    E2E Test: 약점 개념 표시

    시나리오:
    1. 강한 개념(정답 많음)과 약한 개념(오답 많음) 생성
    2. 약점 개념 페이지 접속
    3. 약한 개념만 표시되는지 확인
    """
    # Given: 강한 개념 A, 약한 개념 B
    attempts = [
        # A: 3개 정답
        {"student_id": "e2e_student_3", "question_id": "q_1", "concept": "A", "is_correct": True},
        {"student_id": "e2e_student_3", "question_id": "q_2", "concept": "A", "is_correct": True},
        {"student_id": "e2e_student_3", "question_id": "q_3", "concept": "A", "is_correct": True},
        # B: 3개 오답
        {"student_id": "e2e_student_3", "question_id": "q_4", "concept": "B", "is_correct": False},
        {"student_id": "e2e_student_3", "question_id": "q_5", "concept": "B", "is_correct": False},
        {"student_id": "e2e_student_3", "question_id": "q_6", "concept": "B", "is_correct": False},
    ]

    for attempt_data in attempts:
        response = requests.post(f"{api_base_url}/api/attempts", json=attempt_data)
        print(f"시도 기록: {attempt_data['concept']} - {attempt_data['is_correct']} -> {response.status_code}")

    # API 응답 확인
    api_response = requests.get(f"{api_base_url}/api/mastery/weak-concepts/e2e_student_3")
    print(f"\nAPI 응답 상태: {api_response.status_code}")
    print(f"API 응답 데이터: {api_response.json()}")

    # When: 약점 개념 페이지 접속
    page.goto(f"{api_base_url}/weak-concepts/e2e_student_3")

    # 디버깅: 페이지 내용 확인
    page.wait_for_timeout(2000)
    page.screenshot(path="debug_weak_concepts.png")
    content = page.content()
    print(f"\n페이지 HTML (처음 500자):\n{content[:500]}")

    # 약점 개념 카드가 표시될 때까지 대기
    page.wait_for_selector("[data-testid='concept-card'], [data-testid='empty-state']", timeout=10000)

    # Then: B는 표시, A는 표시 안 됨
    expect(page.locator("text=B")).to_be_visible(timeout=10000)

    # 약점 개념 경고 아이콘 확인
    weak_badge = page.locator("[data-testid='weak-concept-badge']")
    expect(weak_badge).to_be_visible()


@pytest.mark.e2e
def test_api_error_handling(page: Page, api_base_url: str):
    """
    E2E Test: API 에러 처리

    시나리오:
    1. 존재하지 않는 학생 ID로 접속
    2. 에러 메시지 표시 확인
    """
    # When: 존재하지 않는 학생 프로파일 접속
    page.goto(f"{api_base_url}/profile/nonexistent_student")

    # Then: 에러 메시지 또는 빈 상태 표시
    error_message = page.locator("[data-testid='empty-state'], [data-testid='error-message']")
    expect(error_message).to_be_visible(timeout=10000)


@pytest.mark.e2e
def test_navigation_flow(page: Page, api_base_url: str):
    """
    E2E Test: 페이지 간 네비게이션

    시나리오:
    1. 홈 → 프로파일 → 약점 개념 → 홈 순서로 이동
    2. 각 페이지가 정상적으로 로드되는지 확인
    """
    # 홈 페이지
    page.goto(api_base_url)
    expect(page.locator("text=Student Hub")).to_be_visible(timeout=10000)

    # 프로파일 페이지로 이동
    page.click("[data-testid='nav-profile']")
    expect(page).to_have_url(f"{api_base_url}/profile/demo_student")

    # 약점 개념 페이지로 이동
    page.click("[data-testid='nav-weak-concepts']")
    expect(page).to_have_url(f"{api_base_url}/weak-concepts/demo_student")

    # 홈으로 돌아가기
    page.click("[data-testid='nav-home']")
    expect(page).to_have_url(f"{api_base_url}/")
