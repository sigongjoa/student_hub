# Node 0 (Student Hub) - 시스템 인덱스

> 이 문서는 Claude Code가 코드베이스 전체를 스캔하지 않고도 시스템을 이해할 수 있도록 하는 핵심 인덱스입니다.

**마지막 업데이트**: 2026-01-12
**현재 진행**: Week 2 (MCP Tools & Workflow Engine 구현 중)

---

## 📋 시스템 개요

**Node 0 (Student Hub)**는 Mathesis 플랫폼의 Master Orchestrator로, 5개의 핵심 워크플로우를 관리합니다.

- **아키텍처**: gRPC + PostgreSQL + MCP (Mock/Real 모드 전환 가능)
- **개발 방식**: TDD (Test-Driven Development)
- **완료율**: Week 1 완료 (100%), Week 2 진행 중 (~20%)

---

## 🗂️ 디렉토리 구조 및 역할

### `/app` - 메인 애플리케이션
```
app/
├── main.py                    # FastAPI 서버 진입점
├── config.py                  # 전역 설정 (DB, Redis, MCP 경로)
├── db/                        # 데이터베이스 설정
│   ├── base.py                # SQLAlchemy Base
│   └── session.py             # AsyncSession 관리
├── models/                    # SQLAlchemy ORM 모델
│   ├── student.py             # 학생 모델
│   ├── conversation.py        # 대화/메시지 모델
│   ├── workflow_template.py   # 워크플로우 템플릿
│   ├── custom_tool.py         # 커스텀 MCP 툴
│   ├── workflow_session.py    # 워크플로우 실행 세션
│   └── student_attempt.py     # 학생 문제 풀이 기록
├── repositories/              # Repository 패턴 (100% 실제 DB)
│   ├── student_repository.py
│   ├── conversation_repository.py
│   ├── workflow_template_repository.py
│   └── custom_tool_repository.py
├── services/                  # 비즈니스 로직
│   ├── weekly_diagnostic_service.py      # 주간 진단
│   ├── error_review_service.py           # 오답 복습
│   ├── learning_path_service.py          # 학습 경로
│   ├── exam_prep_service.py              # 시험 준비
│   ├── mastery_service.py                # 숙련도 계산
│   └── workflow_engine.py                # 워크플로우 엔진
├── mcp/                       # MCP 클라이언트 및 Mock 서버
│   ├── manager.py             # MCP 클라이언트 매니저 (싱글톤)
│   ├── client.py              # MCP 클라이언트 (stdio/mock 모드)
│   ├── mock_node2_qdna.py     # Mock Q-DNA (BKT, 문제 추천)
│   ├── mock_node4_labnode.py  # Mock Lab Node (활동 데이터)
│   ├── mock_node7_errornote.py # Mock Error Note (오답노트, Anki)
│   └── tools/                 # MCP Tools (5개)
│       ├── analyze_weaknesses.py
│       ├── error_review.py
│       ├── learning_path.py
│       ├── exam_prep.py
│       └── student_profile.py
└── routers/                   # FastAPI 라우터
    ├── workflows.py           # 워크플로우 API
    └── attempts.py            # 학생 시도 API
```

### `/tests` - 테스트 (140개, 100% 통과)
```
tests/
├── conftest.py                # pytest 픽스처 (db_session, mock_mcp 등)
├── test_database_connection.py # DB 연결 테스트
├── unit/                      # 단위 테스트 (123개)
│   ├── test_student_repository.py (13개)
│   ├── test_conversation_repository.py (12개)
│   ├── test_workflow_template_repository.py (12개)
│   ├── test_custom_tool_repository.py (12개)
│   ├── test_bkt_algorithm.py
│   ├── test_irt_algorithm.py
│   ├── test_mastery_service.py
│   └── test_workflow_engine.py
└── integration/               # 통합 테스트 (17개)
    ├── test_mock_mcp_servers.py (17개)
    └── test_weekly_diagnostic_service.py (Week 2)
```

### `/docs` - 문서
```
docs/
├── SYSTEM_INDEX.md            # 이 파일 (시스템 전체 인덱스)
├── COMPONENT_GUIDE.md         # 컴포넌트별 상세 가이드
├── WEEK1_COMPLETION_REPORT.md # Week 1 완료 보고서
├── OPTION3_TDD_ROADMAP.md     # 8-10주 TDD 로드맵
└── IMPLEMENTATION_STATUS.md   # 구현 상태
```

---

## 🔑 핵심 컴포넌트 빠른 참조

### 1. Database Layer (100% 실제 구현)
- **위치**: `app/repositories/`
- **상태**: Week 1 완료, 49개 테스트 통과
- **상세**: `docs/COMPONENT_GUIDE.md#repositories`

### 2. Mock MCP Servers (100% 구현)
- **위치**: `app/mcp/mock_*.py`
- **상태**: Week 1 완료, 17개 테스트 통과
- **기능**:
  - Node 2 (Q-DNA): BKT, 문제 추천, 학습 시간 추정
  - Node 4 (Lab Node): 활동 데이터, 히트맵, 약점 분석
  - Node 7 (Error Note): 오답노트, Anki SM-2 알고리즘
- **상세**: `docs/COMPONENT_GUIDE.md#mock-mcp-servers`

### 3. MCP Tools (5개, Week 2 진행 중)
- **위치**: `app/mcp/tools/`
- **상태**: 구조 완성, 실제 연동 진행 중
- **상세**: `docs/COMPONENT_GUIDE.md#mcp-tools`

### 4. Services (비즈니스 로직)
- **위치**: `app/services/`
- **상태**: 기본 구현 완료, Week 2에서 Mock MCP 연동 중
- **상세**: `docs/COMPONENT_GUIDE.md#services`

### 5. Workflow Engine
- **위치**: `app/services/workflow_engine.py`
- **상태**: 기본 구현 완료, Week 2에서 5개 워크플로우 통합 예정
- **상세**: `docs/COMPONENT_GUIDE.md#workflow-engine`

---

## 🚀 5가지 워크플로우

### 1. Weekly Diagnostic (주간 진단)
- **파일**: `app/services/weekly_diagnostic_service.py`
- **MCP Tools**: `analyze_weaknesses.py`
- **데이터 플로우**: Node 0 → Node 4 (활동) → Node 2 (BKT) → Node 2 (문제 추천)
- **상태**: Week 2 진행 중 (Mock MCP 연동 테스트 작성 완료)

### 2. Error Review (오답 복습)
- **파일**: `app/services/error_review_service.py`
- **MCP Tools**: `error_review.py`
- **데이터 플로우**: Node 0 → Node 4 (오답) → Node 7 (오답노트) → Node 7 (Anki)
- **상태**: Week 2 예정

### 3. Learning Path (학습 경로)
- **파일**: `app/services/learning_path_service.py`
- **MCP Tools**: `learning_path.py`
- **데이터 플로우**: Node 0 → Node 4 (히트맵) → Node 1 (선수지식) → Node 2 (경로)
- **상태**: Week 2 예정

### 4. Class Management (클래스 관리)
- **파일**: (미구현)
- **MCP Tools**: (미구현)
- **상태**: Week 3 예정

### 5. Exam Preparation (시험 준비)
- **파일**: `app/services/exam_prep_service.py`
- **MCP Tools**: `exam_prep.py`
- **데이터 플로우**: Node 0 → Node 6 (학교) → Node 4 (약점) → Node 2 (문제)
- **상태**: Week 3 예정

---

## 📊 현재 진행 상황

### ✅ 완료 (Week 1)
- PostgreSQL 설정 및 연결
- 4개 Repository (Student, Conversation, WorkflowTemplate, CustomTool)
- 3개 Mock MCP 서버 (Node 2, 4, 7)
- 140개 테스트 (100% 통과)

### 🔄 진행 중 (Week 2)
- MCP Tools와 Mock MCP 서버 연동
- WeeklyDiagnosticService 통합 테스트
- MCPClientManager 개선 (Mock 서버 인스턴스 사용)

### 📅 예정 (Week 2-3)
- 5개 MCP Tools 완전 구현
- Workflow Engine 통합
- E2E 테스트

---

## 🔍 코드 탐색 가이드

### 특정 기능을 찾을 때
1. **DB 관련**: `app/repositories/` 확인
2. **비즈니스 로직**: `app/services/` 확인
3. **MCP 통신**: `app/mcp/` 확인
4. **API 엔드포인트**: `app/routers/` 확인
5. **테스트**: `tests/unit/` 또는 `tests/integration/` 확인

### 새로운 기능 추가 시
1. `docs/COMPONENT_GUIDE.md`에서 관련 컴포넌트 확인
2. 해당 컴포넌트의 테스트 파일 확인
3. TDD 방식으로 테스트 먼저 작성 (RED)
4. 구현 (GREEN)
5. 리팩토링 (REFACTOR)

---

## 🛠️ 개발 환경

### 필수 도구
- Python 3.10+
- PostgreSQL 14
- pytest (테스트)

### 실행 명령어
```bash
# 테스트 실행
pytest tests/unit/ -v                    # 단위 테스트
pytest tests/integration/ -v             # 통합 테스트
pytest -v                                # 전체 테스트

# 서버 실행
uvicorn app.main:app --reload            # FastAPI 개발 서버
```

### 환경 변수 (.env)
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=student_hub
POSTGRES_USER=mathesis
POSTGRES_PASSWORD=mathesis2024
USE_MOCK_MCP=True  # False로 변경하면 실제 MCP 서버 사용
```

---

## 📖 추가 참고 문서

- **컴포넌트 상세 가이드**: `docs/COMPONENT_GUIDE.md`
- **Week 1 완료 보고서**: `docs/WEEK1_COMPLETION_REPORT.md`
- **TDD 로드맵**: `docs/OPTION3_TDD_ROADMAP.md`
- **구현 상태**: `docs/IMPLEMENTATION_STATUS.md`

---

## 💡 자주 묻는 질문

### Q: Mock MCP와 Real MCP의 차이는?
**A**: `app/config.py`의 `USE_MOCK_MCP` 설정으로 전환
- `True`: Week 1에서 만든 Mock 서버 사용 (테스트/개발용)
- `False`: 실제 MCP 서버 사용 (stdio 프로토콜)

### Q: Repository는 어떻게 테스트하나요?
**A**: `tests/unit/test_*_repository.py` 참조, TDD RED-GREEN-REFACTOR 사이클

### Q: 새로운 워크플로우를 추가하려면?
**A**:
1. `app/services/` 에 새 서비스 생성
2. `tests/integration/` 에 통합 테스트 작성
3. `app/mcp/tools/` 에 새 MCP Tool 추가 (필요시)

### Q: 전체 시스템을 이해하려면?
**A**:
1. 이 파일 (SYSTEM_INDEX.md) 먼저 읽기
2. `docs/COMPONENT_GUIDE.md` 읽기
3. `docs/WEEK1_COMPLETION_REPORT.md` 읽기 (구현 상세)
