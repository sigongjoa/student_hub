# 컴포넌트 상세 가이드

> 각 컴포넌트의 역할, API, 사용 예제를 상세히 설명합니다.

---

## 📦 Repositories

### StudentRepository
**파일**: `app/repositories/student_repository.py`
**테스트**: `tests/unit/test_student_repository.py` (13개)

**주요 메서드**:
- `create(name, grade, school_id)` - 학생 생성
- `get_by_id(student_id)` - ID로 조회
- `list_students(skip, limit, school_id, grade)` - 목록 조회 (페이지네이션)
- `update(student_id, **kwargs)` - 정보 수정
- `delete(student_id)` - 삭제
- `count_by_school(school_id)` - 학교별 카운트
- `exists(student_id)` - 존재 여부

**사용 예제**:
```python
from app.repositories.student_repository import StudentRepository

repo = StudentRepository(db_session)
student = await repo.create("김철수", 10, "school_001")
```

---

### ConversationRepository
**파일**: `app/repositories/conversation_repository.py`
**테스트**: `tests/unit/test_conversation_repository.py` (12개)

**주요 메서드**:
- `create_conversation(student_id, title)` - 대화 생성
- `get_conversation_with_messages(conversation_id)` - 메시지 포함 조회
- `add_message(conversation_id, role, content)` - 메시지 추가
- `get_messages_by_conversation(conversation_id)` - 메시지 목록
- `delete_conversation(conversation_id)` - 대화 삭제 (CASCADE)

**사용 예제**:
```python
from app.repositories.conversation_repository import ConversationRepository

repo = ConversationRepository(db_session)
conv = await repo.create_conversation("student_001", "수학 질문")
msg = await repo.add_message(conv.id, "user", "도함수가 뭔가요?")
```

---

### WorkflowTemplateRepository
**파일**: `app/repositories/workflow_template_repository.py`
**테스트**: `tests/unit/test_workflow_template_repository.py` (12개)

**주요 메서드**:
- `create(name, description, definition, created_by)` - 템플릿 생성
- `list_public_templates()` - 공개 템플릿 목록
- `increment_execution_count(template_id)` - 실행 횟수 증가
- `search_by_name(search_term)` - 이름 검색

**사용 예제**:
```python
from app.repositories.workflow_template_repository import WorkflowTemplateRepository

repo = WorkflowTemplateRepository(db_session)
template = await repo.create(
    name="주간 진단",
    description="학생 약점 진단",
    definition={"nodes": [...], "edges": [...]},
    created_by="teacher_001"
)
```

---

### CustomToolRepository
**파일**: `app/repositories/custom_tool_repository.py`
**테스트**: `tests/unit/test_custom_tool_repository.py` (12개)

**주요 메서드**:
- `create(name, description, input_schema, definition, created_by)` - 툴 생성
- `get_by_name(name)` - 이름으로 조회
- `list_active_tools()` - 활성 툴 목록
- `exists_by_name(name)` - 이름 중복 확인

**사용 예제**:
```python
from app.repositories.custom_tool_repository import CustomToolRepository

repo = CustomToolRepository(db_session)
tool = await repo.create(
    name="custom_api_call",
    description="커스텀 API 호출",
    input_schema='{"type": "object", ...}',
    definition={"type": "http_request", ...},
    created_by="teacher_001"
)
```

---

## 🤖 Mock MCP Servers

### MockNode2QDNA (Q-DNA)
**파일**: `app/mcp/mock_node2_qdna.py`
**테스트**: `tests/integration/test_mock_mcp_servers.py`

**기능**:
- BKT 기반 숙련도 계산
- 문제 추천 (IRT 기반)
- 문제 DNA 정보 제공
- 학습 시간 추정

**주요 메서드**:
- `get_student_mastery(student_id, concepts)` - 숙련도 조회
- `recommend_questions(student_id, concept, difficulty, count)` - 문제 추천
- `get_question_dna(question_id)` - 문제 DNA
- `estimate_learning_time(concept, current_mastery, target_mastery)` - 시간 추정

**사용 예제**:
```python
from app.mcp.mock_node2_qdna import MockNode2QDNA

node2 = MockNode2QDNA()
mastery = await node2.get_student_mastery("student_001", ["도함수", "적분"])
# {"도함수": 0.45, "적분": 0.55}

questions = await node2.recommend_questions("student_001", "도함수", "medium", 10)
# [{"id": "q_1", "content": "...", "difficulty": "medium", ...}, ...]
```

---

### MockNode4LabNode (Lab Node)
**파일**: `app/mcp/mock_node4_labnode.py`
**테스트**: `tests/integration/test_mock_mcp_servers.py`

**기능**:
- 학생 활동 데이터 제공
- 개념별 히트맵
- 약점 개념 분석
- 클래스 분석

**주요 메서드**:
- `get_recent_concepts(student_id, days)` - 최근 학습 개념
- `get_concept_heatmap(student_id)` - 개념 히트맵
- `get_weak_concepts(student_id, threshold, limit)` - 약점 개념
- `get_student_activity_summary(student_id)` - 활동 요약
- `get_class_analytics(class_id)` - 클래스 분석

**사용 예제**:
```python
from app.mcp.mock_node4_labnode import MockNode4LabNode

node4 = MockNode4LabNode()
heatmap = await node4.get_concept_heatmap("student_001")
# {"극한": 0.45, "도함수": 0.55, "적분": 0.35, ...}

weak = await node4.get_weak_concepts("student_001", threshold=0.6, limit=3)
# [{"concept": "적분", "accuracy": 0.35, "attempts": 10}, ...]
```

---

### MockNode7ErrorNote (Error Note)
**파일**: `app/mcp/mock_node7_errornote.py`
**테스트**: `tests/integration/test_mock_mcp_servers.py`

**기능**:
- 오답노트 CRUD
- Anki SM-2 스케줄링 알고리즘
- 복습 예정 노트 관리

**주요 메서드**:
- `create_error_note(student_id, question_id, student_answer, correct_answer)` - 오답노트 생성
- `get_error_note(error_note_id)` - 오답노트 조회
- `list_error_notes_by_student(student_id)` - 학생별 목록
- `calculate_anki_schedule(error_note_id, quality)` - Anki 스케줄 계산
- `get_due_reviews(student_id, date)` - 복습 예정 노트

**사용 예제**:
```python
from app.mcp.mock_node7_errornote import MockNode7ErrorNote

node7 = MockNode7ErrorNote()
error_note = await node7.create_error_note(
    student_id="student_001",
    question_id="q_001",
    student_answer="잘못된 답",
    correct_answer="정답"
)
# {"id": "en_...", "analysis": {...}, "anki_data": {...}}

anki = await node7.calculate_anki_schedule(error_note["id"], quality=5)
# {"ease_factor": 2.6, "interval_days": 6, "next_review": "..."}
```

---

## 🔧 MCP Tools

### analyze_weaknesses.py
**역할**: 학생 약점 분석 및 주간 진단 워크플로우 실행
**상태**: 구조 완성, Week 2에서 Mock MCP 연동 중

**Input Schema**:
```json
{
  "student_id": "string (required)",
  "curriculum_path": "string (required)",
  "include_weak_concepts": "boolean (default: true)"
}
```

**Output**:
```json
{
  "workflow_id": "wf_...",
  "weak_concepts": ["개념1", "개념2"],
  "questions": [...],
  "total_estimated_time_minutes": 30
}
```

---

### error_review.py
**역할**: 오답 복습 워크플로우 실행
**상태**: Week 2 예정

**Input Schema**:
```json
{
  "student_id": "string (required)",
  "question_id": "string (required)",
  "student_answer": "string (required)",
  "correct_answer": "string (required)"
}
```

---

### learning_path.py
**역할**: 개인화 학습 경로 생성
**상태**: Week 2 예정

**Input Schema**:
```json
{
  "student_id": "string (required)",
  "target_concept": "string (required)",
  "days": "integer (required)"
}
```

---

### exam_prep.py
**역할**: 시험 준비 워크플로우 실행
**상태**: Week 3 예정

**Input Schema**:
```json
{
  "student_id": "string (required)",
  "exam_date": "string (required)",
  "school_id": "string (required)",
  "curriculum_paths": "array of string"
}
```

---

### student_profile.py
**역할**: 학생 통합 프로필 조회
**상태**: Week 2 예정

**Input Schema**:
```json
{
  "student_id": "string (required)"
}
```

---

## 🔄 Services (비즈니스 로직)

### WeeklyDiagnosticService
**파일**: `app/services/weekly_diagnostic_service.py`
**상태**: Mock MCP 연동 중

**데이터 플로우**:
1. Node 4 (Lab Node) - 최근 학습 개념 조회
2. Node 2 (Q-DNA) - BKT 숙련도 조회
3. 약점 개념 식별 (숙련도 < 0.6)
4. Node 2 (Q-DNA) - 문제 추천
5. WorkflowSession 생성

**사용 예제**:
```python
from app.services.weekly_diagnostic_service import WeeklyDiagnosticService, WeeklyDiagnosticRequest

service = WeeklyDiagnosticService(mcp_manager, db_session)
request = WeeklyDiagnosticRequest(
    student_id="student_001",
    curriculum_path="중학수학.2학년.1학기",
    include_weak_concepts=True
)
result = await service.start_diagnostic(request)
```

---

### ErrorReviewService
**파일**: `app/services/error_review_service.py`
**상태**: Week 2 예정

**데이터 플로우**:
1. Node 4 (Lab Node) - 오답 감지
2. Node 7 (Error Note) - 오답노트 생성
3. Node 7 (Error Note) - Anki 스케줄링

---

### LearningPathService
**파일**: `app/services/learning_path_service.py`
**상태**: Week 2 예정

**데이터 플로우**:
1. Node 4 (Lab Node) - 히트맵 조회
2. Node 1 (Logic Engine) - 선수지식 그래프
3. Topological Sort - 학습 순서 결정
4. Node 2 (Q-DNA) - 학습 시간 추정

---

## ⚙️ Configuration

### app/config.py
**주요 설정**:
```python
# Database
POSTGRES_HOST = "localhost"
POSTGRES_DB = "student_hub"
POSTGRES_USER = "mathesis"

# MCP Mode
USE_MOCK_MCP = True  # False로 변경 시 실제 MCP 서버 사용

# gRPC Ports
GRPC_PORT = 50050  # 기존 서비스
GRPC_MCP_PORT = 50051  # 새로운 대화형 시스템
```

---

## 🧪 Testing

### Fixtures (tests/conftest.py)
**주요 픽스처**:
- `db_session` - AsyncSession (테스트용 DB)
- `mock_mcp` - MockMCPManager
- `sample_student` - 샘플 학생 데이터
- `sample_workflow_session` - 샘플 워크플로우 세션

**사용 예제**:
```python
@pytest.mark.asyncio
async def test_example(db_session, mock_mcp):
    # db_session과 mock_mcp를 사용한 테스트
    pass
```

---

## 📝 개발 패턴

### TDD Cycle
1. **RED**: 실패하는 테스트 작성
2. **GREEN**: 최소한의 코드로 테스트 통과
3. **REFACTOR**: 코드 개선

### Repository 패턴
- 모든 DB 접근은 Repository를 통해
- SQLAlchemy Async 사용
- 트랜잭션 관리는 Service에서

### MCP 통신 패턴
```python
# MCPClientManager 사용
mcp = MCPClientManager(use_mock=True)
await mcp.initialize()

# MCP 호출
result = await mcp.call("q-dna", "get_student_mastery", {
    "student_id": "student_001",
    "concepts": ["도함수", "적분"]
})
```

---

## 🔗 관련 문서

- **시스템 인덱스**: `docs/SYSTEM_INDEX.md`
- **Week 1 완료 보고서**: `docs/WEEK1_COMPLETION_REPORT.md`
- **TDD 로드맵**: `docs/OPTION3_TDD_ROADMAP.md`
