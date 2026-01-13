#!/usr/bin/env python3
"""
User Manual Screenshot Generator

각 워크플로우별로 실제 UI 스크린샷을 촬영하고 크롭하여 유저 매뉴얼 생성
"""
import asyncio
from playwright.async_api import async_playwright, Page
import json
from PIL import Image
import os

# 매뉴얼 디렉토리 생성
MANUAL_DIR = "user_manual"
SCREENSHOTS_DIR = f"{MANUAL_DIR}/screenshots"

async def setup_directories():
    """디렉토리 설정"""
    os.makedirs(MANUAL_DIR, exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    print(f"✅ Directories created: {MANUAL_DIR}, {SCREENSHOTS_DIR}")

def crop_screenshot(input_path: str, output_path: str, box: tuple):
    """스크린샷 크롭"""
    img = Image.open(input_path)
    cropped = img.crop(box)
    cropped.save(output_path)
    print(f"   📐 Cropped: {output_path}")

async def phase1_weekly_diagnostic(page: Page):
    """Phase 1: Weekly Diagnostic 매뉴얼 스크린샷"""
    print("\n" + "="*80)
    print("📊 Phase 1: Weekly Diagnostic - 스크린샷 촬영")
    print("="*80)

    screenshots = {}

    # 1. 대시보드에서 시작
    print("\n1️⃣ Step 1: 대시보드 초기 화면")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase1_step1_dashboard.png")
    screenshots['step1'] = "phase1_step1_dashboard.png"
    print("   ✅ Dashboard screenshot saved")

    # 2. Students 페이지로 이동
    print("\n2️⃣ Step 2: Students 페이지 접근")
    students_link = page.locator("text=Students").first
    await students_link.click()
    await page.wait_for_url("**/students")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase1_step2_students_page.png")
    screenshots['step2'] = "phase1_step2_students_page.png"
    print("   ✅ Students page screenshot saved")

    # 3. 학생 생성 (API)
    print("\n3️⃣ Step 3: 학생 생성")
    response = await page.request.post(
        "http://localhost:8000/api/v1/students",
        data=json.dumps({
            "name": "김민수 (매뉴얼 테스트)",
            "grade": 10,
            "school_id": "서울고등학교"
        }),
        headers={"Content-Type": "application/json"}
    )
    student = await response.json()
    student_id = student['id']
    print(f"   ✅ Student created: {student['name']} ({student_id})")

    # 페이지 새로고침하여 학생 표시
    await page.reload()
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase1_step3_student_created.png")
    screenshots['step3'] = "phase1_step3_student_created.png"

    # 4. Weekly Diagnostic API 호출
    print("\n4️⃣ Step 4: Weekly Diagnostic 실행")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/weekly-diagnostic",
        data=json.dumps({
            "student_id": student_id,
            "curriculum_path": "고등수학.1학년.미적분",
            "include_weak_concepts": True
        }),
        headers={"Content-Type": "application/json"}
    )
    diagnostic = await response.json()

    # 결과를 JSON 파일로 저장
    with open(f"{SCREENSHOTS_DIR}/phase1_result.json", "w", encoding="utf-8") as f:
        json.dump(diagnostic, f, ensure_ascii=False, indent=2)

    print(f"   ✅ Workflow ID: {diagnostic['workflow_id']}")
    print(f"   📝 Questions: {len(diagnostic['questions'])}개")
    print(f"   ⚠️  Weak concepts: {', '.join(diagnostic['weak_concepts'])}")

    # 5. 결과 시각화 (API 응답을 화면에 표시하는 간단한 HTML 생성)
    print("\n5️⃣ Step 5: 결과 확인")
    result_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #4F46E5; }}
            .stat {{ background: #EEF2FF; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .question {{ background: #F9FAFB; padding: 10px; margin: 5px 0; border-left: 3px solid #4F46E5; }}
            .weak {{ background: #FEE2E2; padding: 10px; margin: 5px 0; border-left: 3px solid #DC2626; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 주간 진단 결과</h1>
            <div class="stat">
                <strong>학생:</strong> {student['name']} (Grade {student['grade']})<br>
                <strong>Workflow ID:</strong> {diagnostic['workflow_id']}<br>
                <strong>시작 시간:</strong> {diagnostic['started_at']}
            </div>
            <h2>⚠️ 약점 개념 ({len(diagnostic['weak_concepts'])}개)</h2>
            {''.join([f'<div class="weak">• {concept}</div>' for concept in diagnostic['weak_concepts']])}
            <h2>📝 추천 문제 ({len(diagnostic['questions'])}개)</h2>
            {''.join([f'<div class="question"><strong>Q{i+1}:</strong> {q["content"]} <br><small>난이도: {q["difficulty"]}, 개념: {", ".join(q["concepts"])}</small></div>' for i, q in enumerate(diagnostic['questions'][:5])])}
            <div class="stat">
                <strong>⏱️ 예상 소요 시간:</strong> {diagnostic['total_estimated_time_minutes']}분
            </div>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase1_result.html", "w", encoding="utf-8") as f:
        f.write(result_html)

    # HTML 결과 화면 캡처
    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase1_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase1_step5_result.png")
    screenshots['step5'] = "phase1_step5_result.png"
    print("   ✅ Result screenshot saved")

    return screenshots, student_id

async def phase2_error_review(page: Page, student_id: str):
    """Phase 2: Error Review 매뉴얼 스크린샷"""
    print("\n" + "="*80)
    print("❌ Phase 2: Error Review - 스크린샷 촬영")
    print("="*80)

    screenshots = {}

    # 1. 문제 상황 시뮬레이션
    print("\n1️⃣ Step 1: 오답 상황")
    problem_html = """
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            h1 { color: #DC2626; }
            .problem { background: #F9FAFB; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .answer { background: #FEE2E2; padding: 15px; margin: 10px 0; border-left: 3px solid #DC2626; }
            .correct { background: #D1FAE5; padding: 15px; margin: 10px 0; border-left: 3px solid #10B981; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❌ 틀린 문제</h1>
            <div class="problem">
                <strong>문제:</strong> f(x) = x² + 3x의 도함수를 구하시오.
            </div>
            <div class="answer">
                <strong>학생 답변:</strong> f'(x) = x² + 3
            </div>
            <div class="correct">
                <strong>정답:</strong> f'(x) = 2x + 3
            </div>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase2_step1_problem.html", "w", encoding="utf-8") as f:
        f.write(problem_html)

    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase2_step1_problem.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase2_step1_problem.png")
    screenshots['step1'] = "phase2_step1_problem.png"
    print("   ✅ Problem screenshot saved")

    # 2. Error Review API 호출
    print("\n2️⃣ Step 2: 오답 분석 실행")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/error-review",
        data=json.dumps({
            "student_id": student_id,
            "question_id": "q_manual_derivative_001",
            "student_answer": "f'(x) = x² + 3",
            "correct_answer": "f'(x) = 2x + 3"
        }),
        headers={"Content-Type": "application/json"}
    )
    error_review = await response.json()

    print(f"   ✅ Error Note ID: {error_review['error_note_id']}")
    print(f"   🔍 Analysis: {error_review['analysis']['misconception']}")

    # 3. 결과 시각화
    print("\n3️⃣ Step 3: 분석 결과 및 복습 스케줄")
    result_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #DC2626; }}
            .analysis {{ background: #FEF3C7; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #F59E0B; }}
            .schedule {{ background: #DBEAFE; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #3B82F6; }}
            .concept {{ background: #F3E8FF; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            strong {{ color: #1F2937; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 AI 오답 분석 결과</h1>
            <p><strong>오답노트 ID:</strong> {error_review['error_note_id']}</p>

            <div class="analysis">
                <h3>📋 분석</h3>
                <p><strong>오개념:</strong><br>{error_review['analysis']['misconception']}</p>
                <p><strong>근본 원인:</strong><br>{error_review['analysis']['root_cause']}</p>
                <h4>관련 개념:</h4>
                {''.join([f'<div class="concept">• {c}</div>' for c in error_review['analysis']['related_concepts']])}
            </div>

            <div class="schedule">
                <h3>📅 Anki 복습 스케줄</h3>
                <p><strong>다음 복습일:</strong> {error_review['next_review_date']}</p>
                <p><strong>복습 간격:</strong> {error_review['anki_interval_days']}일</p>
                <p style="background: #FEF3C7; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    💡 <strong>팁:</strong> 꾸준한 복습으로 장기 기억으로 전환됩니다!
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase2_step3_result.html", "w", encoding="utf-8") as f:
        f.write(result_html)

    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase2_step3_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase2_step3_result.png")
    screenshots['step3'] = "phase2_step3_result.png"
    print("   ✅ Result screenshot saved")

    return screenshots

async def phase3_learning_path(page: Page, student_id: str):
    """Phase 3: Learning Path 매뉴얼 스크린샷"""
    print("\n" + "="*80)
    print("🗺️  Phase 3: Learning Path - 스크린샷 촬영")
    print("="*80)

    screenshots = {}

    # 1. 목표 설정 화면
    print("\n1️⃣ Step 1: 학습 목표 설정")
    goal_html = """
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            h1 { color: #8B5CF6; }
            .input-group { margin: 15px 0; }
            label { display: block; font-weight: bold; margin-bottom: 5px; }
            input { width: 100%; padding: 10px; border: 1px solid #D1D5DB; border-radius: 5px; }
            select { width: 100%; padding: 10px; border: 1px solid #D1D5DB; border-radius: 5px; }
            .btn { background: #8B5CF6; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ 개인화 학습 경로 생성</h1>
            <div class="input-group">
                <label>목표 개념:</label>
                <input type="text" value="적분" readonly>
            </div>
            <div class="input-group">
                <label>학습 기간:</label>
                <select>
                    <option>14일</option>
                </select>
            </div>
            <button class="btn">🚀 학습 경로 생성</button>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase3_step1_goal.html", "w", encoding="utf-8") as f:
        f.write(goal_html)

    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase3_step1_goal.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase3_step1_goal.png")
    screenshots['step1'] = "phase3_step1_goal.png"
    print("   ✅ Goal setting screenshot saved")

    # 2. Learning Path API 호출
    print("\n2️⃣ Step 2: AI 학습 경로 생성")
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

    print(f"   ✅ Workflow ID: {learning_path['workflow_id']}")
    print(f"   📚 Path length: {len(learning_path['learning_path'])} concepts")

    # 3. 결과 시각화
    print("\n3️⃣ Step 3: 학습 경로 및 일일 플랜")

    # 경로 다이어그램 생성
    path_items = []
    for i, node in enumerate(learning_path['learning_path']):
        prereq = f"<small>선수: {', '.join(node['prerequisites'])}</small>" if node['prerequisites'] else "<small>선수 없음</small>"
        arrow = "⬇️" if i < len(learning_path['learning_path']) - 1 else ""
        path_items.append(f"""
        <div class="path-node">
            <div class="node-number">{node['order']}</div>
            <div class="node-content">
                <strong>{node['concept']}</strong><br>
                {prereq}<br>
                <span class="hours">⏱️ {node['estimated_hours']}시간</span>
            </div>
        </div>
        {f'<div class="arrow">{arrow}</div>' if arrow else ''}
        """)

    result_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #8B5CF6; }}
            .path-container {{ background: #F5F3FF; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .path-node {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #8B5CF6; display: flex; align-items: center; }}
            .node-number {{ background: #8B5CF6; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; }}
            .node-content {{ flex: 1; }}
            .hours {{ color: #8B5CF6; font-weight: bold; }}
            .arrow {{ text-align: center; font-size: 24px; margin: 5px 0; }}
            .daily-plan {{ background: #EFF6FF; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .day {{ background: white; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            .stat {{ background: #F0FDF4; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #10B981; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ 개인화 학습 경로</h1>

            <div class="stat">
                <strong>총 학습 시간:</strong> {learning_path['total_estimated_hours']}시간<br>
                <strong>학습 기간:</strong> 14일
            </div>

            <h2>📚 선수지식 기반 학습 순서</h2>
            <div class="path-container">
                {''.join(path_items)}
            </div>

            <h2>📅 일일 학습 플랜</h2>
            <div class="daily-plan">
                {''.join([f'<div class="day"><strong>{day}:</strong> {hours}시간</div>' for day, hours in sorted(learning_path['daily_tasks'].items(), key=lambda x: int(x[0].split()[1]))])}
            </div>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase3_step3_result.html", "w", encoding="utf-8") as f:
        f.write(result_html)

    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase3_step3_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase3_step3_result.png")
    screenshots['step3'] = "phase3_step3_result.png"
    print("   ✅ Result screenshot saved")

    return screenshots

async def phase4_exam_prep(page: Page, student_id: str):
    """Phase 4: Exam Prep 매뉴얼 스크린샷"""
    print("\n" + "="*80)
    print("📝 Phase 4: Exam Preparation - 스크린샷 촬영")
    print("="*80)

    screenshots = {}

    # 1. 시험 정보 입력
    print("\n1️⃣ Step 1: 시험 정보 입력")
    from datetime import datetime, timedelta
    exam_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    input_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #EF4444; }}
            .input-group {{ margin: 15px 0; }}
            label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #D1D5DB; border-radius: 5px; }}
            .btn {{ background: #EF4444; color: white; padding: 12px 24px; border: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 시험 준비 2주 전략</h1>
            <div class="input-group">
                <label>시험일:</label>
                <input type="date" value="{exam_date}" readonly>
            </div>
            <div class="input-group">
                <label>학교:</label>
                <input type="text" value="서울고등학교" readonly>
            </div>
            <div class="input-group">
                <label>시험 범위:</label>
                <input type="text" value="고등수학.1학년.미적분" readonly>
            </div>
            <button class="btn">🚀 2주 학습 플랜 생성</button>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase4_step1_input.html", "w", encoding="utf-8") as f:
        f.write(input_html)

    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase4_step1_input.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase4_step1_input.png")
    screenshots['step1'] = "phase4_step1_input.png"
    print("   ✅ Input screenshot saved")

    # 2. Exam Prep API 호출
    print("\n2️⃣ Step 2: 2주 학습 플랜 생성")
    response = await page.request.post(
        "http://localhost:8000/api/v1/workflows/exam-prep",
        data=json.dumps({
            "student_id": student_id,
            "exam_date": exam_date,
            "school_id": "서울고등학교",
            "curriculum_paths": ["고등수학.1학년.미적분"]
        }),
        headers={"Content-Type": "application/json"}
    )
    exam_prep = await response.json()

    print(f"   ✅ Workflow ID: {exam_prep['workflow_id']}")
    print(f"   📅 Plan length: {len(exam_prep['two_week_plan'])} days")

    # 3. 결과 시각화
    print("\n3️⃣ Step 3: 2주 학습 플랜 및 모의고사")

    # Week 1, Week 2로 분리
    week1 = exam_prep['two_week_plan'][:7]
    week2 = exam_prep['two_week_plan'][7:]

    week1_html = '<br>'.join([
        f"<div class='day-plan'><strong>Day {day['day_number']}</strong> ({day['date']}): {', '.join(day['concepts_to_review'][:2])} | {len(day['practice_problems'])}문제, Anki {day['anki_reviews']}개</div>"
        for day in week1
    ])

    week2_html = '<br>'.join([
        f"<div class='day-plan'><strong>Day {day['day_number']}</strong> ({day['date']}): {', '.join(day['concepts_to_review'][:2])} | {len(day['practice_problems'])}문제, Anki {day['anki_reviews']}개</div>"
        for day in week2
    ])

    result_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            h1 {{ color: #EF4444; }}
            .focus {{ background: #FEE2E2; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #EF4444; }}
            .week {{ background: #F3F4F6; padding: 20px; margin: 15px 0; border-radius: 8px; }}
            .week h3 {{ color: #374151; margin-top: 0; }}
            .day-plan {{ background: white; padding: 10px; margin: 8px 0; border-radius: 4px; border-left: 3px solid #3B82F6; }}
            .mock-exam {{ background: #DBEAFE; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
            .mock-exam a {{ color: #2563EB; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 시험 준비 2주 전략</h1>

            <div class="focus">
                <strong>🎯 집중 공략 개념:</strong> {', '.join(exam_prep['focus_concepts'])}
            </div>

            <div class="week">
                <h3>📆 Week 1: 약점 집중 공략</h3>
                {week1_html}
            </div>

            <div class="week">
                <h3>📆 Week 2: 실전 연습 & 모의고사</h3>
                {week2_html}
            </div>

            <div class="mock-exam">
                <h3>📄 모의고사 PDF</h3>
                <p><a href="{exam_prep['mock_exam_pdf_url']}" target="_blank">🔗 모의고사 다운로드</a></p>
                <small>Day 12-13에 모의고사를 풀어보세요!</small>
            </div>
        </div>
    </body>
    </html>
    """

    with open(f"{SCREENSHOTS_DIR}/phase4_step3_result.html", "w", encoding="utf-8") as f:
        f.write(result_html)

    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/phase4_step3_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/phase4_step3_result.png")
    screenshots['step3'] = "phase4_step3_result.png"
    print("   ✅ Result screenshot saved")

    return screenshots

async def main():
    """메인 실행"""
    print("="*80)
    print("📚 User Manual Screenshot Generator")
    print("="*80)

    await setup_directories()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1024})
        page = await context.new_page()

        try:
            # Phase 1: Weekly Diagnostic
            phase1_screenshots, student_id = await phase1_weekly_diagnostic(page)

            # Phase 2: Error Review
            phase2_screenshots = await phase2_error_review(page, student_id)

            # Phase 3: Learning Path
            phase3_screenshots = await phase3_learning_path(page, student_id)

            # Phase 4: Exam Prep
            phase4_screenshots = await phase4_exam_prep(page, student_id)

            print("\n" + "="*80)
            print("✅ All screenshots generated successfully!")
            print("="*80)
            print(f"\n📁 Screenshots location: {SCREENSHOTS_DIR}/")
            print("\nGenerated files:")
            for phase, screenshots in [
                ("Phase 1", phase1_screenshots),
                ("Phase 2", phase2_screenshots),
                ("Phase 3", phase3_screenshots),
                ("Phase 4", phase4_screenshots)
            ]:
                print(f"\n{phase}:")
                for step, filename in screenshots.items():
                    print(f"  - {step}: {filename}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
