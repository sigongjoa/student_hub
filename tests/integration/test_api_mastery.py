"""
Integration Tests for Mastery API

실제 FastAPI 서버를 구동하고 HTTP 요청으로 테스트

Test Coverage:
- POST /api/mastery/calculate - 숙련도 계산
- GET /api/mastery/profile/{student_id} - 프로파일 조회
- GET /api/mastery/weak-concepts/{student_id} - 약점 개념 조회
- GET /api/attempts/{student_id}/{concept} - 시도 기록 조회
"""
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.integration
@pytest.mark.asyncio
async def test_calculate_mastery_api(api_client, db_session):
    """
    Test: POST /api/mastery/calculate
    Expected: 201 Created, 숙련도 계산 결과 반환
    """
    from app.models.student_attempt import StudentAttempt

    # Given: 시도 기록 생성
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="이차방정식", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="이차방정식", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When: API 호출
    response = await api_client.post(
        "/api/mastery/calculate",
        json={
            "student_id": "student_1",
            "concept": "이차방정식"
        }
    )

    # Then
    assert response.status_code == 200
    data = response.json()
    assert "student_id" in data
    assert "concept" in data
    assert "mastery" in data
    assert data["student_id"] == "student_1"
    assert data["concept"] == "이차방정식"
    assert 0.0 <= data["mastery"] <= 1.0
    assert data["mastery"] > 0.5  # 2개 정답이므로 높은 숙련도


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_mastery_profile_api(api_client, db_session):
    """
    Test: GET /api/mastery/profile/{student_id}
    Expected: 200 OK, 전체 숙련도 프로파일 반환
    """
    from app.models.student_attempt import StudentAttempt

    # Given
    attempts = [
        StudentAttempt(student_id="student_1", question_id="q_1", concept="A", is_correct=True),
        StudentAttempt(student_id="student_1", question_id="q_2", concept="B", is_correct=False),
        StudentAttempt(student_id="student_1", question_id="q_3", concept="C", is_correct=True),
    ]
    for attempt in attempts:
        db_session.add(attempt)
    await db_session.commit()

    # When
    response = await api_client.get("/api/mastery/profile/student_1")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert "student_id" in data
    assert "profile" in data
    assert len(data["profile"]) == 3
    assert "A" in data["profile"]
    assert "B" in data["profile"]
    assert "C" in data["profile"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_weak_concepts_api(api_client, db_session):
    """
    Test: GET /api/mastery/weak-concepts/{student_id}
    Expected: 200 OK, 약점 개념 리스트 반환
    """
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
    response = await api_client.get("/api/mastery/weak-concepts/student_1?threshold=0.5")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert "student_id" in data
    assert "threshold" in data
    assert "weak_concepts" in data

    # 약점 개념이 객체 배열 형식인지 확인
    weak_concepts = data["weak_concepts"]
    assert isinstance(weak_concepts, list)
    assert len(weak_concepts) > 0

    # B는 약점이어야 함
    concept_names = [item["concept"] for item in weak_concepts]
    assert "B" in concept_names
    assert "A" not in concept_names

    # 숙련도 값이 포함되어 있는지 확인
    for item in weak_concepts:
        assert "concept" in item
        assert "mastery" in item
        assert 0.0 <= item["mastery"] < 0.5


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_student_attempts_api(api_client, db_session):
    """
    Test: GET /api/attempts/{student_id}/{concept}
    Expected: 200 OK, 시도 기록 리스트 반환
    """
    from app.models.student_attempt import StudentAttempt
    from datetime import datetime, timedelta

    # Given
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
    response = await api_client.get("/api/attempts/student_1/이차방정식")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert "student_id" in data
    assert "concept" in data
    assert "attempts" in data
    assert len(data["attempts"]) == 2
    # 최신 순 정렬
    assert data["attempts"][0]["question_id"] == "q_2"
    assert data["attempts"][1]["question_id"] == "q_1"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_attempt_api(api_client):
    """
    Test: POST /api/attempts
    Expected: 201 Created, 시도 기록 생성
    """
    # When
    response = await api_client.post(
        "/api/attempts",
        json={
            "student_id": "student_1",
            "question_id": "q_999",
            "concept": "삼각함수",
            "is_correct": True,
            "response_time_ms": 35000
        }
    )

    # Then
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "student_1"
    assert data["question_id"] == "q_999"
    assert data["concept"] == "삼각함수"
    assert data["is_correct"] is True
    assert data["response_time_ms"] == 35000
    assert "id" in data
    assert "attempted_at" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_not_found(api_client):
    """
    Test: 존재하지 않는 엔드포인트
    Expected: 404 Not Found
    """
    response = await api_client.get("/api/nonexistent")
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_validation_error(api_client):
    """
    Test: 잘못된 요청 데이터
    Expected: 422 Unprocessable Entity
    """
    response = await api_client.post(
        "/api/mastery/calculate",
        json={
            "student_id": "student_1"
            # concept 누락
        }
    )
    assert response.status_code == 422
