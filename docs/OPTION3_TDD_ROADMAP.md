# Option 3: 완전 실제 구현 - TDD 로드맵

**목표**: 100% 실제 동작하는 시스템 (Mock 0%)
**방법론**: Test-Driven Development (Red-Green-Refactor)
**예상 기간**: 8-10주
**상태**: 🚀 시작

---

## 🎯 TDD 원칙

### Red-Green-Refactor 사이클

```
1. RED: 실패하는 테스트 작성
   ├─ 요구사항을 테스트로 명시
   └─ 테스트 실행 → 실패 확인 (아직 구현 없음)

2. GREEN: 최소한의 코드로 테스트 통과
   ├─ 가장 간단한 방법으로 구현
   └─ 테스트 실행 → 통과 확인

3. REFACTOR: 코드 개선
   ├─ 중복 제거, 구조 개선
   └─ 테스트 여전히 통과하는지 확인
```

### 품질 기준

- ✅ 모든 기능은 테스트로 검증됨
- ✅ 테스트 커버리지 80% 이상
- ✅ Mock 데이터 0%
- ✅ 실제 DB 사용
- ✅ 실제 MCP 서버 통신
- ✅ E2E 테스트 통과

---

## 📋 전체 로드맵 (8-10주)

### Week 1-2: 기반 구축
- PostgreSQL + Redis 설정
- DB 모델 및 Repository 패턴 (TDD)
- Mock MCP 서버 구현 (Node 2, 4, 7)

### Week 3-4: MCP Tools 실제 구현 (1/2)
- Tool 1: get_student_profile (TDD)
- Tool 2: analyze_student_weaknesses (TDD)

### Week 5-6: MCP Tools 실제 구현 (2/2)
- Tool 3: create_error_review (TDD)
- Tool 4: generate_learning_path (TDD)
- Tool 5: prepare_exam (TDD)

### Week 7: Workflow Execution Engine 통합
- ExecuteWorkflowTemplate 실제 구현 (TDD)
- Streaming 이벤트 실제 전송
- DB에 실행 기록 저장

### Week 8: E2E 통합 테스트
- 전체 시스템 통합 테스트
- Chat → LLM → gRPC → MCP → DB 전체 플로우
- Performance 테스트

### Week 9-10: Production 준비
- Docker Compose 환경
- 로깅 및 모니터링
- 에러 처리 강화
- 문서화

---

## 🚀 Phase 1: 기반 구축 (Week 1-2)

### Day 1-2: PostgreSQL 설정

#### 1.1 PostgreSQL 설치 및 DB 생성

**테스트 작성 (tests/test_database_connection.py)**
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

@pytest.mark.asyncio
async def test_database_connection():
    """PostgreSQL 연결 테스트"""
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        assert result.scalar() == 1

    await engine.dispose()

@pytest.mark.asyncio
async def test_create_tables():
    """테이블 생성 테스트"""
    from app.db.base import Base

    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 테이블 존재 확인
    async with engine.begin() as conn:
        result = await conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public'"
        )
        tables = [row[0] for row in result]

        assert "students" in tables
        assert "conversations" in tables
        assert "messages" in tables
        assert "workflow_templates" in tables
        assert "custom_tools" in tables

    await engine.dispose()
```

**실행**
```bash
# RED: 테스트 실행 (실패 예상)
pytest tests/test_database_connection.py -v

# PostgreSQL 설치 및 설정
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# DB 생성
sudo -u postgres psql << EOF
CREATE DATABASE student_hub;
CREATE USER mathesis WITH PASSWORD 'mathesis2024';
GRANT ALL PRIVILEGES ON DATABASE student_hub TO mathesis;
\q
EOF

# GREEN: 테스트 재실행 (통과)
pytest tests/test_database_connection.py -v
```

#### 1.2 Alembic 마이그레이션 테스트

**테스트 작성 (tests/test_alembic_migrations.py)**
```python
import pytest
from alembic import command
from alembic.config import Config

def test_alembic_upgrade():
    """Alembic upgrade 테스트"""
    alembic_cfg = Config("alembic.ini")

    # 모든 마이그레이션 실행
    command.upgrade(alembic_cfg, "head")

    # Downgrade 테스트
    command.downgrade(alembic_cfg, "base")

    # 다시 upgrade
    command.upgrade(alembic_cfg, "head")
```

---

### Day 3-4: Repository 패턴 구현 (TDD)

#### 2.1 Student Repository

**테스트 작성 (tests/unit/test_student_repository.py)**
```python
import pytest
from app.repositories.student_repository import StudentRepository
from app.models.student import Student

@pytest.mark.asyncio
async def test_create_student(db_session):
    """학생 생성 테스트"""
    repo = StudentRepository(db_session)

    student = await repo.create(
        name="김철수",
        grade=10,
        school_id="school_001"
    )

    assert student.id is not None
    assert student.name == "김철수"
    assert student.grade == 10

@pytest.mark.asyncio
async def test_get_student(db_session):
    """학생 조회 테스트"""
    repo = StudentRepository(db_session)

    # Create
    created = await repo.create(name="김영희", grade=11, school_id="school_001")

    # Get
    retrieved = await repo.get(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "김영희"

@pytest.mark.asyncio
async def test_list_students(db_session):
    """학생 목록 조회 테스트"""
    repo = StudentRepository(db_session)

    # Create multiple
    await repo.create(name="학생1", grade=10, school_id="school_001")
    await repo.create(name="학생2", grade=11, school_id="school_001")
    await repo.create(name="학생3", grade=10, school_id="school_002")

    # List all
    all_students = await repo.list()
    assert len(all_students) >= 3

    # List with filter
    school1_students = await repo.list(school_id="school_001")
    assert len(school1_students) == 2

@pytest.mark.asyncio
async def test_update_student(db_session):
    """학생 정보 수정 테스트"""
    repo = StudentRepository(db_session)

    student = await repo.create(name="김민수", grade=10, school_id="school_001")

    updated = await repo.update(student.id, grade=11)

    assert updated.grade == 11
    assert updated.name == "김민수"  # 변경 안됨

@pytest.mark.asyncio
async def test_delete_student(db_session):
    """학생 삭제 테스트"""
    repo = StudentRepository(db_session)

    student = await repo.create(name="김삭제", grade=10, school_id="school_001")

    success = await repo.delete(student.id)
    assert success == True

    # 조회 시 None
    deleted = await repo.get(student.id)
    assert deleted is None
```

**구현 (app/repositories/student_repository.py)**
```python
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import Student

class StudentRepository:
    """학생 Repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, grade: int, school_id: str) -> Student:
        """학생 생성"""
        student = Student(name=name, grade=grade, school_id=school_id)
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student

    async def get(self, student_id: str) -> Optional[Student]:
        """학생 조회"""
        return await self.session.get(Student, student_id)

    async def list(
        self,
        school_id: Optional[str] = None,
        grade: Optional[int] = None
    ) -> List[Student]:
        """학생 목록 조회"""
        stmt = select(Student)

        if school_id:
            stmt = stmt.where(Student.school_id == school_id)
        if grade:
            stmt = stmt.where(Student.grade == grade)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, student_id: str, **kwargs) -> Student:
        """학생 정보 수정"""
        student = await self.get(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        for key, value in kwargs.items():
            setattr(student, key, value)

        await self.session.commit()
        await self.session.refresh(student)
        return student

    async def delete(self, student_id: str) -> bool:
        """학생 삭제"""
        student = await self.get(student_id)
        if not student:
            return False

        await self.session.delete(student)
        await self.session.commit()
        return True
```

**실행**
```bash
# RED: 테스트 실행 (실패)
pytest tests/unit/test_student_repository.py -v

# GREEN: 구현 후 테스트 (통과)
pytest tests/unit/test_student_repository.py -v

# REFACTOR: 코드 개선 후 다시 테스트
```

---

### Day 5-7: Mock MCP 서버 구현

#### 3.1 Node 2 (Q-DNA) Mock 서버

**요구사항:**
- BKT 숙련도 계산
- 문제 추천
- 학습 경로 생성

**테스트 작성 (tests/mock_servers/test_node2_mock.py)**
```python
import pytest
import grpc
from tests.mock_servers.node2_mock_server import Node2MockServer

@pytest.mark.asyncio
async def test_calculate_mastery():
    """BKT 숙련도 계산 테스트"""
    server = Node2MockServer()
    await server.start()

    # gRPC 클라이언트로 호출
    async with grpc.aio.insecure_channel('localhost:50052') as channel:
        stub = ...  # Node2 stub

        response = await stub.CalculateMastery(
            CalculateMasteryRequest(
                student_id="student_001",
                concept="이차방정식",
                attempts=[...]
            )
        )

        assert 0.0 <= response.mastery_score <= 1.0
        assert response.concept == "이차방정식"

    await server.stop()

@pytest.mark.asyncio
async def test_recommend_questions():
    """문제 추천 테스트"""
    # ... 유사한 패턴
```

**Mock 서버 구현 (tests/mock_servers/node2_mock_server.py)**
```python
import grpc
from concurrent import futures
import random

class Node2MockServer:
    """Node 2 (Q-DNA) Mock gRPC Server"""

    def __init__(self, port=50052):
        self.port = port
        self.server = None

    async def start(self):
        """서버 시작"""
        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10)
        )

        # Servicer 등록
        node2_pb2_grpc.add_QDNAServiceServicer_to_server(
            QDNAMockServicer(), self.server
        )

        self.server.add_insecure_port(f'[::]:{self.port}')
        await self.server.start()

    async def stop(self):
        """서버 종료"""
        if self.server:
            await self.server.stop(grace=5)

class QDNAMockServicer:
    """Q-DNA Mock Servicer"""

    async def CalculateMastery(self, request, context):
        """BKT 숙련도 계산 (Mock)"""
        # 간단한 알고리즘으로 Mock 구현
        correct_count = sum(1 for a in request.attempts if a.is_correct)
        total_count = len(request.attempts)

        if total_count == 0:
            mastery_score = 0.5
        else:
            # 정답률 기반 숙련도
            accuracy = correct_count / total_count
            # BKT 간략 버전: P(L) = P(L0) + (1-P(L0)) * P(T) * correct_ratio
            mastery_score = 0.3 + 0.7 * accuracy

        return CalculateMasteryResponse(
            concept=request.concept,
            mastery_score=mastery_score,
            attempts_count=total_count
        )

    async def RecommendQuestions(self, request, context):
        """문제 추천 (Mock)"""
        # 개념 기반 Mock 문제 생성
        questions = []

        for i in range(request.count):
            questions.append(Question(
                id=f"q_mock_{request.concept}_{i}",
                content=f"{request.concept} 관련 문제 {i+1}",
                difficulty=self._calculate_difficulty(request.mastery_score),
                concepts=[request.concept]
            ))

        return RecommendQuestionsResponse(questions=questions)

    def _calculate_difficulty(self, mastery_score):
        """숙련도 기반 난이도 결정"""
        if mastery_score < 0.4:
            return "easy"
        elif mastery_score < 0.7:
            return "medium"
        else:
            return "hard"
```

---

### Day 8-10: Node 4, 7 Mock 서버 구현

**동일한 TDD 패턴으로:**
- Node 4 (Lab Node): 학습 활동 데이터
- Node 7 (Error Note): 오답노트 및 Anki

---

## 🔧 Phase 2: MCP Tools 실제 구현 (Week 3-6)

### Tool 1: get_student_profile (Week 3, Day 1-2)

#### Step 1: 통합 테스트 작성 (RED)

**tests/integration/test_get_student_profile_tool.py**
```python
import pytest
from app.mcp.tools import TOOL_REGISTRY

@pytest.mark.asyncio
async def test_get_student_profile_full_integration(
    db_session,
    node2_mock_server,
    node4_mock_server
):
    """get_student_profile Tool 전체 통합 테스트"""

    # Given: DB에 학생 데이터 존재
    from app.repositories.student_repository import StudentRepository
    repo = StudentRepository(db_session)
    student = await repo.create(
        name="김철수",
        grade=10,
        school_id="school_001"
    )

    # Given: Node 4에 활동 데이터 존재 (Mock)
    # Given: Node 2에 숙련도 데이터 존재 (Mock)

    # When: Tool 실행
    tool = TOOL_REGISTRY["get_student_profile"]
    result = await tool.execute({
        "student_id": student.id
    })

    # Then: 실제 통합 데이터 반환
    assert result["student"]["id"] == student.id
    assert result["student"]["name"] == "김철수"
    assert "mastery" in result
    assert "activity" in result
    assert "error_notes" in result

    # Then: 숙련도 데이터가 실제로 계산됨 (Mock 서버에서)
    assert isinstance(result["mastery"]["concept_scores"], dict)
    assert len(result["mastery"]["concept_scores"]) > 0

    # Then: 활동 데이터가 실제로 조회됨 (Mock 서버에서)
    assert result["activity"]["total_attempts"] >= 0
    assert result["activity"]["overall_accuracy"] >= 0.0
```

#### Step 2: 구현 (GREEN)

**app/mcp/tools/student_profile.py**
```python
async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    학생 프로필 조회 - 실제 구현

    1. DB에서 학생 기본 정보 조회
    2. Node 4에서 최근 활동 데이터 조회
    3. Node 2에서 숙련도 계산
    4. Node 7에서 오답 노트 조회
    5. 통합하여 반환
    """
    from app.repositories.student_repository import StudentRepository
    from app.mcp.manager import MCPClientManager
    from app.db.session import get_db_context

    student_id = arguments["student_id"]

    # 1. DB에서 학생 조회
    async with get_db_context() as db:
        repo = StudentRepository(db)
        student = await repo.get(student_id)

        if not student:
            raise ValueError(f"Student {student_id} not found")

    # 2. MCP 클라이언트 초기화
    mcp = MCPClientManager()

    # 3. Node 4에서 활동 데이터 조회
    activity_data = await mcp.call(
        node="lab-node",
        tool="get_student_activities",
        params={
            "student_id": student_id,
            "days": 30
        }
    )

    # 4. Node 2에서 숙련도 계산
    mastery_data = await mcp.call(
        node="q-dna",
        tool="calculate_mastery_profile",
        params={
            "student_id": student_id,
            "activities": activity_data["activities"]
        }
    )

    # 5. Node 7에서 오답 노트 조회
    error_notes = await mcp.call(
        node="error-note",
        tool="get_error_notes",
        params={
            "student_id": student_id,
            "limit": 10
        }
    )

    # 6. 통합 반환
    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "grade": student.grade,
            "school_id": student.school_id
        },
        "mastery": {
            "concept_scores": mastery_data["concept_scores"],
            "overall_score": mastery_data["overall_score"]
        },
        "activity": {
            "total_attempts": activity_data["total_attempts"],
            "total_correct": activity_data["total_correct"],
            "overall_accuracy": activity_data["overall_accuracy"],
            "active_days": activity_data["active_days"]
        },
        "error_notes": error_notes["notes"]
    }
```

#### Step 3: 테스트 실행 및 검증

```bash
# RED: 첫 실행 (실패 예상)
pytest tests/integration/test_get_student_profile_tool.py -v

# 구현 진행...

# GREEN: 테스트 통과
pytest tests/integration/test_get_student_profile_tool.py -v
# ✅ test_get_student_profile_full_integration PASSED

# REFACTOR: 코드 개선
# - 에러 처리 추가
# - 로깅 추가
# - 타임아웃 처리

# 다시 테스트 (여전히 통과하는지 확인)
pytest tests/integration/test_get_student_profile_tool.py -v
```

---

### Tool 2-5: 동일한 TDD 패턴 반복

각 Tool마다:
1. **RED**: 통합 테스트 작성 (실패)
2. **GREEN**: 최소 구현 (통과)
3. **REFACTOR**: 코드 개선 (여전히 통과)

**예상 일정:**
- Tool 2 (analyze_student_weaknesses): 3-4일
- Tool 3 (create_error_review): 2-3일
- Tool 4 (generate_learning_path): 3-4일
- Tool 5 (prepare_exam): 3-4일

---

## 🔄 Phase 3: Workflow Execution (Week 7)

### 실제 워크플로우 실행 통합 테스트

**tests/integration/test_workflow_execution_real.py**
```python
@pytest.mark.asyncio
async def test_execute_real_workflow_with_real_tools(
    db_session,
    node2_mock_server,
    node4_mock_server,
    grpc_stub
):
    """실제 도구를 사용한 워크플로우 실행 테스트"""

    # Given: 학생 데이터
    repo = StudentRepository(db_session)
    student = await repo.create(...)

    # Given: 워크플로우 템플릿
    template_def = {
        "nodes": [
            {
                "id": "node1",
                "type": "tool",
                "tool_name": "get_student_profile",
                "config": {"student_id": "{{input.student_id}}"}
            },
            {
                "id": "node2",
                "type": "tool",
                "tool_name": "analyze_student_weaknesses",
                "config": {
                    "student_id": "{{input.student_id}}",
                    "curriculum_path": "중학수학.2학년"
                }
            }
        ],
        "edges": [{"from": "node1", "to": "node2"}]
    }

    # When: 워크플로우 실행
    events = []
    async for event in grpc_stub.ExecuteWorkflowTemplate(...):
        events.append(event)

    # Then: 실제 실행 이벤트 확인
    assert events[0].event_type == "started"
    assert events[1].event_type == "node_started"
    assert events[1].node_id == "node1"
    assert events[2].event_type == "node_completed"
    assert events[2].node_id == "node1"

    # Then: 실제 데이터 반환 확인
    node1_result = json.loads(events[2].data)
    assert node1_result["student"]["id"] == student.id
    assert "mastery" in node1_result  # 실제 계산됨

    # Then: 순차 실행 확인
    assert events[3].event_type == "node_started"
    assert events[3].node_id == "node2"

    # Then: 최종 완료
    assert events[-1].event_type == "completed"
```

---

## 📊 진행 상황 추적

### Week별 체크리스트

#### Week 1-2: 기반 구축
- [ ] PostgreSQL 설치 및 테스트
- [ ] Alembic 마이그레이션 테스트
- [ ] Student Repository (TDD)
- [ ] Conversation Repository (TDD)
- [ ] WorkflowTemplate Repository (TDD)
- [ ] Node 2 Mock 서버 (TDD)
- [ ] Node 4 Mock 서버 (TDD)
- [ ] Node 7 Mock 서버 (TDD)

#### Week 3-4: MCP Tools (1/2)
- [ ] get_student_profile 실제 구현 (TDD)
- [ ] analyze_student_weaknesses 실제 구현 (TDD)
- [ ] 통합 테스트 통과
- [ ] Mock 데이터 0% 확인

#### Week 5-6: MCP Tools (2/2)
- [ ] create_error_review 실제 구현 (TDD)
- [ ] generate_learning_path 실제 구현 (TDD)
- [ ] prepare_exam 실제 구현 (TDD)
- [ ] 모든 Tool 테스트 통과

#### Week 7: Workflow Execution
- [ ] ExecuteWorkflowTemplate 실제 구현 (TDD)
- [ ] Streaming 이벤트 실제 전송
- [ ] DB 실행 기록 저장
- [ ] 복잡한 워크플로우 테스트

#### Week 8: E2E 테스트
- [ ] Chat → LLM → gRPC 전체 플로우
- [ ] UI → Backend → DB 전체 플로우
- [ ] Performance 테스트
- [ ] Concurrent 요청 테스트

#### Week 9-10: Production
- [ ] Docker Compose 환경
- [ ] 로깅 및 모니터링
- [ ] 에러 처리 강화
- [ ] 최종 문서화

---

## 🎯 품질 지표

### 테스트 커버리지 목표

| 컴포넌트 | 목표 커버리지 | 현재 |
|---------|--------------|------|
| Repositories | 90% | 0% |
| MCP Tools | 85% | 5% |
| gRPC Services | 80% | 60% |
| Workflow Engine | 90% | 100% |
| 전체 평균 | 85% | 40% |

### Mock 제거 목표

| 컴포넌트 | Mock % (현재) | Mock % (목표) |
|---------|--------------|--------------|
| MCP Tools | 95% | 0% |
| Database | 100% | 0% |
| MCP Servers | 100% | 30%* |
| 전체 | 70% | 10%* |

*Mock MCP 서버는 유지 (실제 Node 2,4,7 구현은 별도 프로젝트)

---

## 🚀 시작하기

### 우선순위 1: PostgreSQL 설정

지금 바로 시작하겠습니다:

1. PostgreSQL 설치
2. 첫 테스트 작성 및 실행
3. DB 연결 확인
4. 첫 Repository TDD

준비되셨나요? 바로 시작하겠습니다! 🎉
