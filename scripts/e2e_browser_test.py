#!/usr/bin/env python3
"""
E2E Browser Test with Playwright

프론트엔드와 백엔드 전체 스택을 실제 브라우저로 테스트합니다.
"""
import asyncio
import sys
from playwright.async_api import async_playwright, Page
import json

async def test_frontend_loaded(page: Page):
    """프론트엔드 페이지가 로드되는지 테스트"""
    print("📄 Testing frontend page load...")

    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    title = await page.title()
    print(f"   ✅ Page loaded: {title}")

    # 페이지 스크린샷 저장
    await page.screenshot(path="test_screenshots/01_frontend_loaded.png")
    print(f"   📸 Screenshot saved: 01_frontend_loaded.png")

async def test_create_student(page: Page):
    """학생 생성 API 테스트"""
    print("\n👨‍🎓 Testing student creation...")

    # REST API 직접 호출 (프론트엔드 UI가 없는 경우)
    response = await page.request.post(
        "http://localhost:8000/api/v1/students",
        data=json.dumps({
            "name": "Playwright 테스트 학생",
            "grade": 11,
            "school_id": "TEST_SCHOOL_001"
        }),
        headers={"Content-Type": "application/json"}
    )

    assert response.ok, f"Failed to create student: {response.status}"
    student_data = await response.json()

    print(f"   ✅ Student created: {student_data['name']} (ID: {student_data['id']})")
    return student_data['id']

async def test_weekly_diagnostic(page: Page, student_id: str):
    """주간 진단 워크플로우 테스트"""
    print("\n📊 Testing Weekly Diagnostic workflow...")

    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/weekly-diagnostic",
        data=json.dumps({
            "student_id": student_id,
            "curriculum_path": "중학수학.2학년.1학기",
            "include_weak_concepts": True
        }),
        headers={"Content-Type": "application/json"}
    )

    assert response.ok, f"Weekly Diagnostic failed: {response.status}"
    result = await response.json()

    print(f"   ✅ Workflow ID: {result['workflow_id']}")
    print(f"   ✅ Questions: {len(result['questions'])} problems")
    print(f"   ✅ Weak concepts: {', '.join(result['weak_concepts'])}")
    print(f"   ✅ Estimated time: {result['total_estimated_time_minutes']} minutes")

    return result

async def test_error_review(page: Page, student_id: str):
    """오답 복습 워크플로우 테스트"""
    print("\n❌ Testing Error Review workflow...")

    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/error-review",
        data=json.dumps({
            "student_id": student_id,
            "question_id": "q_test_001",
            "student_answer": "잘못된 답변",
            "correct_answer": "정답"
        }),
        headers={"Content-Type": "application/json"}
    )

    assert response.ok, f"Error Review failed: {response.status}"
    result = await response.json()

    print(f"   ✅ Error Note ID: {result['error_note_id']}")
    print(f"   ✅ Next review: {result['next_review_date']}")
    print(f"   ✅ Anki interval: {result['anki_interval_days']} days")
    print(f"   ✅ Analysis: {result['analysis']['misconception']}")

    return result

async def test_learning_path(page: Page, student_id: str):
    """학습 경로 생성 워크플로우 테스트"""
    print("\n🗺️  Testing Learning Path workflow...")

    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/learning-path",
        data=json.dumps({
            "student_id": student_id,
            "target_concept": "적분",
            "days": 14
        }),
        headers={"Content-Type": "application/json"}
    )

    assert response.ok, f"Learning Path failed: {response.status}"
    result = await response.json()

    print(f"   ✅ Workflow ID: {result['workflow_id']}")
    print(f"   ✅ Total hours: {result['total_estimated_hours']} hours")
    print(f"   ✅ Learning path:")
    for node in result['learning_path']:
        print(f"      {node['order']}. {node['concept']} ({node['estimated_hours']}h)")

    return result

async def test_exam_prep(page: Page, student_id: str):
    """시험 준비 워크플로우 테스트"""
    print("\n📝 Testing Exam Prep workflow...")

    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/exam-prep",
        data=json.dumps({
            "student_id": student_id,
            "exam_date": "2026-01-24",
            "school_id": "TEST_SCHOOL_001",
            "curriculum_paths": ["중학수학.2학년.1학기"]
        }),
        headers={"Content-Type": "application/json"}
    )

    assert response.ok, f"Exam Prep failed: {response.status}"
    result = await response.json()

    print(f"   ✅ Workflow ID: {result['workflow_id']}")
    print(f"   ✅ Study plan: {len(result['two_week_plan'])} days")
    print(f"   ✅ Focus concepts: {', '.join(result['focus_concepts'])}")
    print(f"   ✅ Mock exam PDF: {result['mock_exam_pdf_url']}")

    # 첫 3일 플랜 출력
    print(f"   ✅ First 3 days:")
    for day in result['two_week_plan'][:3]:
        print(f"      Day {day['day_number']}: {', '.join(day['concepts_to_review'])} ({len(day['practice_problems'])} problems)")

    return result

async def test_health_endpoints(page: Page):
    """헬스 체크 엔드포인트 테스트"""
    print("\n💚 Testing health endpoints...")

    # REST API health
    response = await page.request.get("http://localhost:8000/health")
    assert response.ok
    health_data = await response.json()
    print(f"   ✅ REST API: {health_data['status']}, gRPC: {health_data['grpc']}")

    # Root endpoint
    response = await page.request.get("http://localhost:8000/")
    assert response.ok
    root_data = await response.json()
    print(f"   ✅ Service: {root_data['service']}, Version: {root_data['version']}")

async def main():
    """메인 테스트 실행"""
    print("=" * 80)
    print("🚀 Node 0 Student Hub - E2E Browser Test")
    print("=" * 80)

    async with async_playwright() as p:
        # 브라우저 실행 (headless 모드)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 스크린샷 디렉토리 생성
            import os
            os.makedirs("test_screenshots", exist_ok=True)

            # 1. 프론트엔드 로드 테스트
            await test_frontend_loaded(page)

            # 2. 헬스 체크
            await test_health_endpoints(page)

            # 3. 학생 생성
            student_id = await test_create_student(page)

            # 4. 4가지 워크플로우 테스트
            await test_weekly_diagnostic(page, student_id)
            await test_error_review(page, student_id)
            await test_learning_path(page, student_id)
            await test_exam_prep(page, student_id)

            print("\n" + "=" * 80)
            print("✅ All E2E tests passed!")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            # 에러 발생 시 스크린샷 저장
            await page.screenshot(path="test_screenshots/error.png")
            raise

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
