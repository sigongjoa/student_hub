#!/usr/bin/env python3
"""
Simple User Manual Generator

HTML 기반 시연용 매뉴얼 생성
"""
import asyncio
from playwright.async_api import async_playwright
import os

MANUAL_DIR = "user_manual"
SCREENSHOTS_DIR = f"{MANUAL_DIR}/screenshots"

async def setup():
    os.makedirs(MANUAL_DIR, exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def capture_phase1(page):
    """Phase 1: Weekly Diagnostic"""
    print("\n📊 Phase 1: Weekly Diagnostic")

    # Step 1: Dashboard
    print("  Step 1: Dashboard")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p1_step1_dashboard.png")

    # Step 2: Students page
    print("  Step 2: Students page")
    students_link = page.locator("text=Students").first
    await students_link.click()
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p1_step2_students.png")

    # Step 3: Mock result
    print("  Step 3: Result visualization")
    html = """
    <html><head><style>
    body{font-family:Arial;padding:30px;background:#f5f5f5}
    .container{max-width:900px;margin:0 auto;background:white;padding:40px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
    h1{color:#4F46E5;margin:0 0 30px 0}
    .stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin:30px 0}
    .stat-card{background:#EEF2FF;padding:20px;border-radius:8px;text-align:center}
    .stat-value{font-size:32px;font-weight:bold;color:#4F46E5}
    .stat-label{color:#666;margin-top:8px}
    .weak-concepts{background:#FEE2E2;padding:20px;border-radius:8px;margin:20px 0}
    .weak-concepts h3{color:#DC2626;margin:0 0 15px 0}
    .concept-tag{display:inline-block;background:#DC2626;color:white;padding:8px 16px;border-radius:20px;margin:5px}
    .questions{margin-top:30px}
    .question{background:#F9FAFB;padding:15px;margin:10px 0;border-left:4px solid #4F46E5;border-radius:4px}
    .question strong{color:#1F2937}
    .question small{color:#666}
    </style></head><body>
    <div class="container">
        <h1>📊 주간 진단 결과</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">10</div>
                <div class="stat-label">추천 문제 수</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">20분</div>
                <div class="stat-label">예상 소요 시간</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">2개</div>
                <div class="stat-label">약점 개념</div>
            </div>
        </div>
        <div class="weak-concepts">
            <h3>⚠️ 약점 개념</h3>
            <span class="concept-tag">도함수 (숙련도: 45%)</span>
            <span class="concept-tag">적분 (숙련도: 55%)</span>
        </div>
        <div class="questions">
            <h3>📝 맞춤형 문제 추천</h3>
            <div class="question">
                <strong>문제 1:</strong> f(x) = x² + 3x의 도함수를 구하시오<br>
                <small>난이도: 중급 | 개념: 도함수, 미분</small>
            </div>
            <div class="question">
                <strong>문제 2:</strong> lim(x→2) (x² - 4)/(x - 2)를 구하시오<br>
                <small>난이도: 중급 | 개념: 극한, 부정형</small>
            </div>
            <div class="question">
                <strong>문제 3:</strong> ∫(2x + 1)dx를 계산하시오<br>
                <small>난이도: 기초 | 개념: 적분, 부정적분</small>
            </div>
        </div>
    </div>
    </body></html>
    """
    with open(f"{SCREENSHOTS_DIR}/p1_step3_result.html", "w", encoding="utf-8") as f:
        f.write(html)
    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/p1_step3_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p1_step3_result.png")

async def capture_phase2(page):
    """Phase 2: Error Review"""
    print("\n❌ Phase 2: Error Review")

    # Problem
    print("  Step 1: Problem")
    html = """
    <html><head><style>
    body{font-family:Arial;padding:30px;background:#f5f5f5}
    .container{max-width:700px;margin:0 auto;background:white;padding:40px;border-radius:12px}
    h1{color:#DC2626}
    .problem{background:#F3F4F6;padding:25px;margin:20px 0;border-radius:8px;font-size:18px}
    .student-answer{background:#FEE2E2;padding:20px;margin:15px 0;border-radius:8px;border-left:4px solid #DC2626}
    .correct-answer{background:#D1FAE5;padding:20px;margin:15px 0;border-radius:8px;border-left:4px solid #10B981}
    strong{color:#1F2937}
    </style></head><body>
    <div class="container">
        <h1>❌ 틀린 문제</h1>
        <div class="problem">
            <strong>문제:</strong> f(x) = x² + 3x의 도함수를 구하시오.
        </div>
        <div class="student-answer">
            <strong>학생 답변:</strong> f'(x) = x² + 3
        </div>
        <div class="correct-answer">
            <strong>정답:</strong> f'(x) = 2x + 3
        </div>
    </div>
    </body></html>
    """
    with open(f"{SCREENSHOTS_DIR}/p2_step1_problem.html", "w", encoding="utf-8") as f:
        f.write(html)
    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/p2_step1_problem.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p2_step1_problem.png")

    # Analysis
    print("  Step 2: AI Analysis")
    html = """
    <html><head><style>
    body{font-family:Arial;padding:30px;background:#f5f5f5}
    .container{max-width:800px;margin:0 auto;background:white;padding:40px;border-radius:12px}
    h1{color:#DC2626}
    .analysis{background:#FEF3C7;padding:25px;margin:20px 0;border-radius:8px;border-left:4px solid:#F59E0B}
    .analysis h3{color:#92400E;margin-top:0}
    .schedule{background:#DBEAFE;padding:25px;margin:20px 0;border-radius:8px;border-left:4px solid:#3B82F6}
    .schedule h3{color:#1E40AF;margin-top:0}
    .concept-tag{display:inline-block;background:#A78BFA;color:white;padding:6px 12px;border-radius:15px;margin:5px}
    .tip{background:#FEF3C7;padding:15px;border-radius:6px;margin-top:15px}
    </style></head><body>
    <div class="container">
        <h1>🔍 AI 오답 분석 결과</h1>
        <div class="analysis">
            <h3>📋 오개념 분석</h3>
            <p><strong>오개념:</strong><br>거듭제곱 미분 공식 미숙 - (x^n)' = nx^(n-1) 적용 실패</p>
            <p><strong>근본 원인:</strong><br>상수 계수는 유지되고 지수만 내려온다는 점을 놓침</p>
            <h4>관련 개념:</h4>
            <span class="concept-tag">거듭제곱 미분</span>
            <span class="concept-tag">도함수 기본 공식</span>
            <span class="concept-tag">다항함수 미분</span>
        </div>
        <div class="schedule">
            <h3>📅 Anki 복습 스케줄 (SM-2 알고리즘)</h3>
            <p><strong>다음 복습일:</strong> 내일 (1일 후)</p>
            <p><strong>이후 복습 주기:</strong> 1일 → 3일 → 7일 → 14일 → 30일...</p>
            <div class="tip">
                💡 <strong>팁:</strong> 꾸준한 복습으로 단기 기억을 장기 기억으로 전환합니다!
            </div>
        </div>
    </div>
    </body></html>
    """
    with open(f"{SCREENSHOTS_DIR}/p2_step2_analysis.html", "w", encoding="utf-8") as f:
        f.write(html)
    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/p2_step2_analysis.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p2_step2_analysis.png")

async def capture_phase3(page):
    """Phase 3: Learning Path"""
    print("\n🗺️  Phase 3: Learning Path")

    html = """
    <html><head><style>
    body{font-family:Arial;padding:30px;background:#f5f5f5}
    .container{max-width:900px;margin:0 auto;background:white;padding:40px;border-radius:12px}
    h1{color:#8B5CF6}
    .stat{background:#F0FDF4;padding:20px;margin:20px 0;border-radius:8px;border-left:4px solid:#10B981;font-size:18px}
    .path-container{background:#F5F3FF;padding:30px;border-radius:12px;margin:25px 0}
    .path-node{background:white;padding:20px;margin:15px 0;border-radius:8px;border-left:4px solid:#8B5CF6;display:flex;align-items:center}
    .node-number{background:#8B5CF6;color:white;width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:20px;margin-right:20px;flex-shrink:0}
    .node-content{flex:1}
    .node-content strong{font-size:20px;color:#1F2937}
    .prereq{color:#666;font-size:14px}
    .hours{color:#8B5CF6;font-weight:bold;font-size:16px}
    .arrow{text-align:center;font-size:28px;margin:10px 0;color:#8B5CF6}
    .daily-plan{background:#EFF6FF;padding:25px;border-radius:12px;margin:25px 0}
    .day{background:white;padding:12px;margin:8px 0;border-radius:6px;border-left:3px solid:#3B82F6}
    </style></head><body>
    <div class="container">
        <h1>🗺️ 개인화 학습 경로</h1>
        <div class="stat">
            <strong>총 학습 시간:</strong> 20시간 | <strong>학습 기간:</strong> 14일 | <strong>일평균:</strong> 약 1.5시간
        </div>
        <h2>📚 선수지식 기반 학습 순서</h2>
        <div class="path-container">
            <div class="path-node">
                <div class="node-number">1</div>
                <div class="node-content">
                    <strong>극한</strong><br>
                    <span class="prereq">선수 개념 없음</span><br>
                    <span class="hours">⏱️ 5시간</span>
                </div>
            </div>
            <div class="arrow">⬇️</div>
            <div class="path-node">
                <div class="node-number">2</div>
                <div class="node-content">
                    <strong>도함수</strong><br>
                    <span class="prereq">선수: 극한</span><br>
                    <span class="hours">⏱️ 6시간</span>
                </div>
            </div>
            <div class="arrow">⬇️</div>
            <div class="path-node">
                <div class="node-number">3</div>
                <div class="node-content">
                    <strong>적분</strong><br>
                    <span class="prereq">선수: 도함수</span><br>
                    <span class="hours">⏱️ 9시간</span>
                </div>
            </div>
        </div>
        <h2>📅 14일 학습 플랜</h2>
        <div class="daily-plan">
            <div class="day"><strong>Day 1-2:</strong> 극한 개념 (하루 2.5시간)</div>
            <div class="day"><strong>Day 3-5:</strong> 도함수 기초 (하루 2시간)</div>
            <div class="day"><strong>Day 6-10:</strong> 적분 심화 (하루 1.8시간)</div>
            <div class="day"><strong>Day 11-14:</strong> 종합 복습 및 문제 풀이</div>
        </div>
    </div>
    </body></html>
    """
    with open(f"{SCREENSHOTS_DIR}/p3_result.html", "w", encoding="utf-8") as f:
        f.write(html)
    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/p3_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p3_result.png")

async def capture_phase4(page):
    """Phase 4: Exam Prep"""
    print("\n📝 Phase 4: Exam Preparation")

    html = """
    <html><head><style>
    body{font-family:Arial;padding:30px;background:#f5f5f5}
    .container{max-width:1000px;margin:0 auto;background:white;padding:40px;border-radius:12px}
    h1{color:#EF4444}
    .focus{background:#FEE2E2;padding:20px;margin:20px 0;border-radius:8px;border-left:4px solid:#EF4444}
    .week{background:#F3F4F6;padding:25px;margin:20px 0;border-radius:12px}
    .week h3{color:#374151;margin-top:0}
    .day-plan{background:white;padding:12px;margin:10px 0;border-radius:6px;border-left:3px solid:#3B82F6}
    .phase-label{display:inline-block;background:#8B5CF6;color:white;padding:4px 10px;border-radius:12px;font-size:12px;margin-left:10px}
    .mock-exam{background:#DBEAFE;padding:25px;margin:25px 0;border-radius:12px;text-align:center}
    .mock-exam h3{color:#1E40AF;margin-top:0}
    .btn{display:inline-block;background:#2563EB;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;margin-top:10px}
    </style></head><body>
    <div class="container">
        <h1>📝 시험 준비 2주 전략</h1>
        <div class="focus">
            <strong>🎯 집중 공략 개념:</strong> 도함수, 극한, 적분 (약점 개념 우선 배치)
        </div>
        <div class="week">
            <h3>📆 Week 1: 약점 집중 공략 <span class="phase-label">Phase 1</span></h3>
            <div class="day-plan"><strong>Day 1-2:</strong> 도함수 기본 (매일 8문제 + Anki 복습 5개)</div>
            <div class="day-plan"><strong>Day 3-4:</strong> 극한과 연속 (매일 10문제 + Anki 복습 8개)</div>
            <div class="day-plan"><strong>Day 5-7:</strong> 적분 기초 (매일 12문제 + Anki 복습 10개)</div>
        </div>
        <div class="week">
            <h3>📆 Week 2: 실전 연습 <span class="phase-label">Phase 2-4</span></h3>
            <div class="day-plan"><strong>Day 8-10:</strong> 전범위 복습 (매일 15문제 + Anki 복습 12개)</div>
            <div class="day-plan"><strong>Day 11-12:</strong> 모의고사 풀이 및 해설 <span class="phase-label">Phase 3</span></div>
            <div class="day-plan"><strong>Day 13-14:</strong> 약점 최종 점검 + Anki 집중 복습 <span class="phase-label">Phase 4</span></div>
        </div>
        <div class="mock-exam">
            <h3>📄 AI 생성 모의고사</h3>
            <p>학생의 약점 개념 기반 맞춤형 모의고사</p>
            <a href="#" class="btn">🔗 모의고사 PDF 다운로드</a>
        </div>
    </div>
    </body></html>
    """
    with open(f"{SCREENSHOTS_DIR}/p4_result.html", "w", encoding="utf-8") as f:
        f.write(html)
    await page.goto(f"file://{os.path.abspath(SCREENSHOTS_DIR)}/p4_result.html")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=f"{SCREENSHOTS_DIR}/p4_result.png")

async def main():
    print("="*80)
    print("📚 User Manual Screenshot Generator (Simple Version)")
    print("="*80)

    await setup()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 1000})
        page = await context.new_page()

        try:
            await capture_phase1(page)
            await capture_phase2(page)
            await capture_phase3(page)
            await capture_phase4(page)

            print("\n" + "="*80)
            print("✅ All screenshots generated!")
            print(f"📁 Location: {SCREENSHOTS_DIR}/")
            print("="*80)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
