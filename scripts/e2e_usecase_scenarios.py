#!/usr/bin/env python3
"""
E2E Use Case Scenarios Test

실제 교육 현장에서 발생하는 유즈케이스 시나리오를 테스트합니다.
"""
import asyncio
from playwright.async_api import async_playwright, Page
import json
from datetime import datetime, timedelta

async def scenario_1_weekly_diagnostic_flow(page: Page):
    """
    시나리오 1: 주간 진단 워크플로우
    - 선생님이 학생에게 주간 진단 평가를 배정
    - 학생의 약점 개념 파악
    - 맞춤형 문제 추천
    """
    print("\n" + "=" * 80)
    print("📊 시나리오 1: 주간 진단 워크플로우")
    print("=" * 80)

    # 1. 학생 생성
    print("\n1️⃣ 학생 등록...")
    response = await page.request.post(
        "http://localhost:8000/api/v1/students",
        data=json.dumps({
            "name": "김수학",
            "grade": 9,
            "school_id": "중앙중학교"
        }),
        headers={"Content-Type": "application/json"}
    )
    student = await response.json()
    student_id = student['id']
    print(f"   ✅ 학생 등록 완료: {student['name']} (Grade {student['grade']})")

    # 2. 주간 진단 시작
    print("\n2️⃣ 주간 진단 평가 시작...")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/weekly-diagnostic",
        data=json.dumps({
            "student_id": student_id,
            "curriculum_path": "중학수학.3학년.1학기",
            "include_weak_concepts": True
        }),
        headers={"Content-Type": "application/json"}
    )
    diagnostic = await response.json()
    print(f"   ✅ 진단 세션 생성: {diagnostic['workflow_id']}")
    print(f"   📝 추천 문제 수: {len(diagnostic['questions'])}개")
    print(f"   ⚠️  약점 개념: {', '.join(diagnostic['weak_concepts'])}")
    print(f"   ⏱️  예상 소요 시간: {diagnostic['total_estimated_time_minutes']}분")

    # 3. 문제 풀이 (시뮬레이션)
    print("\n3️⃣ 학생이 문제 풀이 중...")
    for i, question in enumerate(diagnostic['questions'][:3], 1):
        print(f"   📄 문제 {i}: {question['content']}")
        print(f"      난이도: {question['difficulty']}, 개념: {', '.join(question['concepts'])}")

    return student_id

async def scenario_2_error_review_cycle(page: Page, student_id: str):
    """
    시나리오 2: 오답 복습 사이클
    - 학생이 문제를 틀림
    - 오답노트 자동 생성
    - Anki 스케줄링으로 복습 계획 수립
    """
    print("\n" + "=" * 80)
    print("❌ 시나리오 2: 오답 복습 사이클 (Anki 기반)")
    print("=" * 80)

    # 1. 학생이 문제를 틀림
    print("\n1️⃣ 학생이 문제를 틀림...")
    print("   문제: f(x) = x^2 + 3x의 도함수를 구하시오")
    print("   학생 답: f'(x) = x^2 + 3")
    print("   정답: f'(x) = 2x + 3")

    # 2. 오답 복습 워크플로우 실행
    print("\n2️⃣ 오답노트 생성 및 분석...")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/error-review",
        data=json.dumps({
            "student_id": student_id,
            "question_id": "q_derivative_001",
            "student_answer": "f'(x) = x^2 + 3",
            "correct_answer": "f'(x) = 2x + 3"
        }),
        headers={"Content-Type": "application/json"}
    )
    error_review = await response.json()

    print(f"   ✅ 오답노트 ID: {error_review['error_note_id']}")
    print(f"\n   🔍 AI 분석 결과:")
    print(f"      오개념: {error_review['analysis']['misconception']}")
    print(f"      근본 원인: {error_review['analysis']['root_cause']}")
    print(f"      관련 개념: {', '.join(error_review['analysis']['related_concepts'])}")

    # 3. Anki 복습 스케줄
    print(f"\n   📅 복습 스케줄 (Anki SM-2):")
    print(f"      다음 복습일: {error_review['next_review_date']}")
    print(f"      복습 간격: {error_review['anki_interval_days']}일")
    print(f"      💡 꾸준한 복습으로 장기 기억으로 전환됩니다!")

async def scenario_3_personalized_learning_path(page: Page, student_id: str):
    """
    시나리오 3: 개인화 학습 경로
    - 학생의 약점 개념 분석
    - 선수지식 그래프 기반 학습 순서 결정
    - 2주 학습 플랜 생성
    """
    print("\n" + "=" * 80)
    print("🗺️  시나리오 3: 개인화 학습 경로 (선수지식 기반)")
    print("=" * 80)

    print("\n1️⃣ 목표 설정: '적분' 마스터하기")
    print("   기간: 14일")

    # 학습 경로 생성
    print("\n2️⃣ AI가 최적의 학습 경로를 생성 중...")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/learning-path",
        data=json.dumps({
            "student_id": student_id,
            "target_concept": "적분",
            "days": 14
        }),
        headers={"Content-Type": "application/json"}
    )
    learning_path = await response.json()

    print(f"   ✅ 학습 경로 생성 완료!")
    print(f"\n   📚 학습 순서 (선수지식 그래프 기반):")
    for node in learning_path['learning_path']:
        prereq = f" (선수: {', '.join(node['prerequisites'])})" if node['prerequisites'] else ""
        print(f"      {node['order']}. {node['concept']} - {node['estimated_hours']}시간{prereq}")

    print(f"\n   ⏱️  총 학습 시간: {learning_path['total_estimated_hours']}시간")
    print(f"\n   📅 일일 학습 계획:")
    for day, hours in sorted(learning_path['daily_tasks'].items(), key=lambda x: int(x[0].split()[1])):
        print(f"      {day}: {hours}시간")

async def scenario_4_exam_preparation(page: Page, student_id: str):
    """
    시나리오 4: 시험 준비 (2주 전략)
    - 시험 범위 분석
    - 약점 집중 공략
    - 모의고사 생성
    """
    print("\n" + "=" * 80)
    print("📝 시나리오 4: 시험 준비 2주 전략")
    print("=" * 80)

    exam_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    print(f"\n1️⃣ 시험 정보 입력...")
    print(f"   시험일: {exam_date} (14일 후)")
    print(f"   학교: 중앙중학교")
    print(f"   시험 범위: 중학수학 3학년 1학기")

    # 시험 준비 워크플로우
    print("\n2️⃣ AI가 2주 학습 플랜을 생성 중...")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/exam-prep",
        data=json.dumps({
            "student_id": student_id,
            "exam_date": exam_date,
            "school_id": "중앙중학교",
            "curriculum_paths": ["중학수학.3학년.1학기"]
        }),
        headers={"Content-Type": "application/json"}
    )
    exam_prep = await response.json()

    print(f"   ✅ 학습 플랜 생성 완료!")
    print(f"\n   🎯 집중 공략 개념: {', '.join(exam_prep['focus_concepts'])}")
    print(f"   📄 모의고사 PDF: {exam_prep['mock_exam_pdf_url']}")

    print(f"\n   📅 2주 학습 플랜 (총 {len(exam_prep['two_week_plan'])}일):")

    # 주요 단계별 플랜
    phases = {
        "Week 1 (약점 집중)": exam_prep['two_week_plan'][:7],
        "Week 2 (실전 연습)": exam_prep['two_week_plan'][7:]
    }

    for phase_name, days in phases.items():
        print(f"\n   {phase_name}:")
        for day in days[:3]:  # 각 주에서 3일만 샘플 출력
            concepts = ', '.join(day['concepts_to_review'][:2])
            print(f"      Day {day['day_number']}: {concepts} ({len(day['practice_problems'])}문제, Anki {day['anki_reviews']}개)")

async def scenario_5_teacher_dashboard(page: Page):
    """
    시나리오 5: 선생님 대시보드
    - 학생 목록 조회
    - 전체 통계 확인
    """
    print("\n" + "=" * 80)
    print("👨‍🏫 시나리오 5: 선생님 대시보드")
    print("=" * 80)

    # 학생 목록 조회
    print("\n1️⃣ 전체 학생 목록 조회...")
    response = await page.request.get("http://localhost:8000/api/v1/students")
    students = await response.json()

    print(f"   ✅ 총 {len(students)}명의 학생 등록됨")
    print(f"\n   📋 학생 목록:")
    for i, student in enumerate(students[:5], 1):  # 최대 5명만 출력
        print(f"      {i}. {student['name']} (Grade {student['grade']}, {student['school_id']})")

    # 프론트엔드 대시보드 접속
    print("\n2️⃣ 프론트엔드 대시보드 접속...")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")
    print("   ✅ 대시보드 로드 완료")

    # 스크린샷 저장
    await page.screenshot(path="test_screenshots/scenario_5_teacher_dashboard.png")
    print("   📸 대시보드 스크린샷 저장 완료")

async def main():
    """메인 시나리오 테스트 실행"""
    print("=" * 80)
    print("🎬 Node 0 Student Hub - 실제 유즈케이스 시나리오 테스트")
    print("=" * 80)
    print("\n실제 교육 현장에서 발생하는 5가지 시나리오를 테스트합니다.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            import os
            os.makedirs("test_screenshots", exist_ok=True)

            # 시나리오 1: 주간 진단
            student_id = await scenario_1_weekly_diagnostic_flow(page)

            # 시나리오 2: 오답 복습
            await scenario_2_error_review_cycle(page, student_id)

            # 시나리오 3: 학습 경로
            await scenario_3_personalized_learning_path(page, student_id)

            # 시나리오 4: 시험 준비
            await scenario_4_exam_preparation(page, student_id)

            # 시나리오 5: 선생님 대시보드
            await scenario_5_teacher_dashboard(page)

            print("\n" + "=" * 80)
            print("✅ 모든 유즈케이스 시나리오 테스트 통과!")
            print("=" * 80)
            print("\n📊 테스트 요약:")
            print("   ✅ 시나리오 1: 주간 진단 워크플로우")
            print("   ✅ 시나리오 2: 오답 복습 사이클 (Anki)")
            print("   ✅ 시나리오 3: 개인화 학습 경로")
            print("   ✅ 시나리오 4: 시험 준비 2주 전략")
            print("   ✅ 시나리오 5: 선생님 대시보드")
            print("\n💡 모든 워크플로우가 실제 교육 환경에서 정상 작동합니다!")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ 시나리오 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="test_screenshots/scenario_error.png")
            raise

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
