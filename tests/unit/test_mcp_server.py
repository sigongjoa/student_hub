"""
Unit Tests for MCP Server

TDD: MCP 서버의 tool 구현 테스트

MCP Tools:
- calculate_mastery: 학생의 개념 숙련도 계산
- get_mastery_profile: 학생의 전체 숙련도 프로파일 조회
- identify_weak_concepts: 약점 개념 식별
- get_student_attempts: 학생의 시도 기록 조회

Target: 100% code coverage
"""
import pytest
import json


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_mastery_tool(db_session):
    """
    Test: calculate_mastery MCP tool
    Expected: 학생의 개념 숙련도를 JSON으로 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService
    from app.models.student_attempt import StudentAttempt

    # Given: 시도 기록 생성
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="이차방정식", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="이차방정식", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When: MCP tool 호출
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    result = await mcp_server.calculate_mastery(
        student_id="student_1",
        concept="이차방정식"
    )

    # Then
    data = json.loads(result)
    assert "student_id" in data
    assert "concept" in data
    assert "mastery" in data
    assert data["student_id"] == "student_1"
    assert data["concept"] == "이차방정식"
    assert 0.0 <= data["mastery"] <= 1.0
    assert data["mastery"] > 0.5  # 2개 정답이므로 높은 숙련도


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_mastery_profile_tool(db_session):
    """
    Test: get_mastery_profile MCP tool
    Expected: 학생의 전체 숙련도 프로파일을 JSON으로 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService
    from app.models.student_attempt import StudentAttempt

    # Given: 여러 개념에 대한 시도 기록
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="B", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="C", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    result = await mcp_server.get_mastery_profile(student_id="student_1")

    # Then
    data = json.loads(result)
    assert "student_id" in data
    assert "profile" in data
    assert len(data["profile"]) == 3
    assert "A" in data["profile"]
    assert "B" in data["profile"]
    assert "C" in data["profile"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_identify_weak_concepts_tool(db_session):
    """
    Test: identify_weak_concepts MCP tool
    Expected: 약점 개념 리스트를 JSON으로 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService
    from app.models.student_attempt import StudentAttempt

    # Given: 강한 개념과 약한 개념
    attempts = [
        # 개념 A: 강함
        StudentAttempt(student_id="student_1", question_id="q_1", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="A", is_correct=True),
        # 개념 B: 약함
        StudentAttempt(student_id="student_1", question_id="q_4", concept="B", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_5", concept="B", is_correct=False),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    result = await mcp_server.identify_weak_concepts(
        student_id="student_1",
        threshold=0.5
    )

    # Then
    data = json.loads(result)
    assert "student_id" in data
    assert "weak_concepts" in data
    assert isinstance(data["weak_concepts"], list)
    assert "B" in data["weak_concepts"]
    assert "A" not in data["weak_concepts"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_student_attempts_tool(db_session):
    """
    Test: get_student_attempts MCP tool
    Expected: 학생의 시도 기록을 JSON으로 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService
    from app.models.student_attempt import StudentAttempt
    from datetime import datetime, timedelta

    # Given: 시도 기록
    now = datetime.utcnow()
    attempts = [
        StudentAttempt(
            student_id="student_1",
            question_id="q_1",
            concept="이차방정식",
            is_correct=True,
            response_time_ms=30000,
            attempted_at=now - timedelta(days=1)
        ),
        StudentAttempt(
            student_id="student_1",
            question_id="q_2",
            concept="이차방정식",
            is_correct=False,
            response_time_ms=45000,
            attempted_at=now
        ),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    result = await mcp_server.get_student_attempts(
        student_id="student_1",
        concept="이차방정식",
        limit=10
    )

    # Then
    data = json.loads(result)
    assert "student_id" in data
    assert "concept" in data
    assert "attempts" in data
    assert len(data["attempts"]) == 2
    assert data["attempts"][0]["question_id"] == "q_2"  # 최신 순
    assert data["attempts"][1]["question_id"] == "q_1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_mastery_no_attempts(db_session):
    """
    Test: 시도 기록이 없을 때 calculate_mastery
    Expected: 초기 숙련도 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService

    # Given: 빈 데이터베이스
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing(p_init=0.15)
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    # When
    result = await mcp_server.calculate_mastery(
        student_id="student_999",
        concept="존재하지_않는_개념"
    )

    # Then
    data = json.loads(result)
    assert data["mastery"] == pytest.approx(0.15, abs=0.01)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_student_attempts_limit(db_session):
    """
    Test: limit 파라미터로 시도 기록 개수 제한
    Expected: limit 개수만큼만 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService
    from app.models.student_attempt import StudentAttempt

    # Given: 10개의 시도 기록
    for i in range(10):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="개념1",
            is_correct=True
        )
        db_session.add(attempt)
    await db_session.commit()

    # When: limit=3
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    result = await mcp_server.get_student_attempts(
        student_id="student_1",
        concept="개념1",
        limit=3
    )

    # Then
    data = json.loads(result)
    assert len(data["attempts"]) == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_student_attempts_no_limit(db_session):
    """
    Test: limit 없이 시도 기록 조회
    Expected: 모든 시도 기록 반환
    """
    from app.mcp.server import MCPServer
    from app.repositories.student_attempt_repository import StudentAttemptRepository
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.services.mastery_service import MasteryService
    from app.models.student_attempt import StudentAttempt

    # Given: 5개의 시도 기록
    for i in range(5):
        attempt = StudentAttempt(
            student_id="student_1",
            question_id=f"q_{i}",
            concept="개념1",
            is_correct=True
        )
        db_session.add(attempt)
    await db_session.commit()

    # When: limit 없음
    repo = StudentAttemptRepository(db_session)
    bkt = BayesianKnowledgeTracing()
    service = MasteryService(repo, bkt)
    mcp_server = MCPServer(service)

    result = await mcp_server.get_student_attempts(
        student_id="student_1",
        concept="개념1"
        # limit 파라미터 생략
    )

    # Then: 모든 5개 반환
    data = json.loads(result)
    assert len(data["attempts"]) == 5
