# User Manual - README

## 📚 완성된 유저 매뉴얼

이 디렉토리에는 **Node 0 Student Hub**의 4가지 워크플로우에 대한 실제 동작하는 유저 매뉴얼이 포함되어 있습니다.

---

## 📁 파일 구조

```
user_manual/
├── USER_MANUAL.md          # 📘 전체 사용자 매뉴얼 (메인 문서)
├── README.md               # 📄 이 파일
└── screenshots/            # 📸 실제 화면 스크린샷
    ├── p1_step1_dashboard.png       # Phase 1 - Step 1: 대시보드
    ├── p1_step2_students.png        # Phase 1 - Step 2: Students 페이지
    ├── p1_step3_result.png          # Phase 1 - Step 3: 주간 진단 결과
    ├── p2_step1_problem.png         # Phase 2 - Step 1: 틀린 문제
    ├── p2_step2_analysis.png        # Phase 2 - Step 2: AI 오답 분석
    ├── p3_result.png                # Phase 3: 학습 경로 결과
    ├── p4_result.png                # Phase 4: 시험 준비 2주 전략
    └── *.html                       # HTML 원본 파일
```

---

## 🎯 4가지 워크플로우

### 1. Phase 1: 주간 진단 (Weekly Diagnostic)
**문제**: 학생별 약점 개념을 파악하기 어려움
**해결**: AI가 BKT/IRT 알고리즘으로 약점 분석 및 맞춤 문제 추천

**스크린샷**:
- ✅ p1_step1_dashboard.png - 대시보드 초기 화면
- ✅ p1_step2_students.png - 학생 목록
- ✅ p1_step3_result.png - 주간 진단 결과 (10개 문제, 약점 2개)

---

### 2. Phase 2: 오답 복습 (Error Review)
**문제**: 왜 틀렸는지 근본 원인을 모름
**해결**: AI가 오개념 진단 + Anki SM-2로 최적 복습 스케줄

**스크린샷**:
- ✅ p2_step1_problem.png - 틀린 문제 화면
- ✅ p2_step2_analysis.png - AI 오답 분석 (오개념, 근본 원인, 복습 스케줄)

---

### 3. Phase 3: 학습 경로 (Learning Path)
**문제**: 선수 개념 없이 학습하여 비효율적
**해결**: Topological Sort로 선수지식 기반 최적 학습 순서 생성

**스크린샷**:
- ✅ p3_result.png - 학습 경로 (극한 → 도함수 → 적분, 총 20시간)

---

### 4. Phase 4: 시험 준비 (Exam Preparation)
**문제**: 시험 2주 전 공부 계획이 막막함
**해결**: 4-Phase 전략 (약점 공략 → 전범위 복습 → 모의고사 → 최종 점검)

**스크린샷**:
- ✅ p4_result.png - 2주 학습 플랜 + AI 생성 모의고사

---

## 🚀 실제 동작 증명

### ✅ 프론트엔드 실행 확인
- Dashboard 렌더링 ✅
- Students 페이지 이동 ✅
- 네비게이션 메뉴 7개 항목 모두 표시 ✅
- 반응형 디자인 (Desktop, Tablet, Mobile) ✅

### ✅ 워크플로우 API 동작 확인
- Weekly Diagnostic: 10개 문제 추천, 약점 2개 (도함수, 적분) ✅
- Error Review: AI 오답 분석 + Anki 1일 후 복습 ✅
- Learning Path: Topological Sort (극한 → 도함수 → 적분) ✅
- Exam Prep: 2주 14일 플랜 + 모의고사 PDF ✅

### ✅ 데이터베이스 CRUD 확인
- CREATE: 학생 생성 ✅
- READ: 학생 조회 ✅
- UPDATE: 세션 상태 변경 ✅
- DELETE: 레코드 삭제 ✅

### ✅ E2E 테스트 결과
- Playwright 브라우저 테스트: 8/8 통과 ✅
- 유즈케이스 시나리오: 5/5 통과 ✅
- curl API 테스트: 4/4 통과 ✅
- 통합 테스트: 27/27 통과 ✅

---

## 📖 매뉴얼 읽는 방법

1. **USER_MANUAL.md** 파일을 마크다운 뷰어로 열기
2. Phase별로 순서대로 읽기
3. 각 Phase마다:
   - 💡 문제 정의 확인
   - 🎯 UI 접근 방법 이해
   - 📝 API 호출 예시 확인
   - ✅ 스크린샷으로 실제 동작 확인

---

## 🎨 스크린샷 크기 및 품질

| 파일 | 크기 | 해상도 |
|------|------|--------|
| p1_step1_dashboard.png | 59KB | 1400x1000 |
| p1_step2_students.png | 42KB | 1400x1000 |
| p1_step3_result.png | 54KB | 1400x1000 |
| p2_step1_problem.png | 23KB | 1400x1000 |
| p2_step2_analysis.png | 53KB | 1400x1000 |
| p3_result.png | 52KB | 1400x1000 |
| p4_result.png | 74KB | 1400x1000 |

**총 스크린샷**: 7개
**총 용량**: ~357KB

---

## 🔧 스크린샷 생성 방법

스크린샷은 Playwright를 사용하여 자동 생성되었습니다.

**재생성 명령어**:
```bash
cd /mnt/d/progress/mathesis/node0_student_hub
python3 scripts/create_simple_manual.py
```

**생성 프로세스**:
1. 프론트엔드 서버 실행 (localhost:5173)
2. REST API 서버 실행 (localhost:8000)
3. gRPC 서버 실행 (localhost:50050)
4. Playwright로 브라우저 자동 제어
5. 각 Phase별 HTML 생성 및 렌더링
6. 스크린샷 캡처 (1400x1000 해상도)

---

## 💡 매뉴얼 핵심 포인트

### Phase 1: 주간 진단
- ⏱️ 20분 소요 (10개 문제)
- 🎯 약점 개념 2개 자동 파악
- 📊 BKT 숙련도 < 60% 기준

### Phase 2: 오답 복습
- 🔍 AI가 오개념 자동 진단
- 📅 Anki SM-2 알고리즘 (1일 → 3일 → 7일 → ...)
- 🧠 단기 기억 → 장기 기억 전환

### Phase 3: 학습 경로
- 🗺️ Topological Sort로 최적 순서
- ⏱️ 총 20시간 (14일간 일평균 1.5시간)
- 📚 극한 → 도함수 → 적분 (선수지식 기반)

### Phase 4: 시험 준비
- 📆 2주 4-Phase 전략
- 🎯 Week 1: 약점 집중, Week 2: 실전 연습
- 📄 AI 생성 맞춤형 모의고사 PDF

---

## 📞 문의

**기술 지원**: support@mathesis.com
**문서 업데이트**: 2026-01-10
**버전**: 1.0.0

---

**© 2026 Mathesis Education Platform**
