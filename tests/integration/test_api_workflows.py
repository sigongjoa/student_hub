"""
Integration Tests for Workflow API Endpoints

FastAPI 엔드포인트가 제대로 작동하는지 테스트
"""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weekly_diagnostic_endpoint(api_client):
    """
    Test: POST /api/v1/workflows/weekly-diagnostic

    주간 진단 워크플로우 API 엔드포인트 테스트
    """
    # Given
    request_data = {
        "student_id": "student_001",
        "curriculum_path": "중학수학.2학년.1학기",
        "include_weak_concepts": True
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/weekly-diagnostic",
        json=request_data
    )

    # Then
    assert response.status_code == 200
    data = response.json()

    assert "workflow_id" in data
    assert "session_id" in data
    assert "questions" in data
    assert "weak_concepts" in data
    assert "total_estimated_time_minutes" in data
    assert "started_at" in data

    assert isinstance(data["questions"], list)
    assert isinstance(data["weak_concepts"], list)
    assert data["total_estimated_time_minutes"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_review_endpoint(api_client):
    """
    Test: POST /api/v1/workflows/error-review

    오답 복습 워크플로우 API 엔드포인트 테스트
    """
    # Given
    request_data = {
        "student_id": "student_001",
        "question_id": "q_derivative_001",
        "student_answer": "f'(x) = x² + 3",
        "correct_answer": "f'(x) = 2x + 3"
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/error-review",
        json=request_data
    )

    # Then
    assert response.status_code == 200
    data = response.json()

    assert "error_note_id" in data
    assert "next_review_date" in data
    assert "anki_interval_days" in data
    assert "analysis" in data

    assert data["anki_interval_days"] > 0
    assert "misconception" in data["analysis"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_learning_path_endpoint(api_client):
    """
    Test: POST /api/v1/workflows/learning-path

    학습 경로 생성 워크플로우 API 엔드포인트 테스트
    """
    # Given
    request_data = {
        "student_id": "student_001",
        "target_concept": "적분",
        "days": 14
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/learning-path",
        json=request_data
    )

    # Then
    assert response.status_code == 200
    data = response.json()

    assert "workflow_id" in data
    assert "learning_path" in data
    assert "total_estimated_hours" in data
    assert "daily_tasks" in data

    assert isinstance(data["learning_path"], list)
    assert len(data["learning_path"]) > 0
    assert data["total_estimated_hours"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_exam_prep_endpoint(api_client):
    """
    Test: POST /api/v1/workflows/exam-prep

    시험 준비 워크플로우 API 엔드포인트 테스트
    """
    # Given
    request_data = {
        "student_id": "student_001",
        "exam_date": "2026-01-24",
        "school_id": "서울고등학교",
        "curriculum_paths": ["고등수학.1학년.미적분"]
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/exam-prep",
        json=request_data
    )

    # Then
    assert response.status_code == 200
    data = response.json()

    assert "workflow_id" in data
    assert "two_week_plan" in data
    assert "practice_problems" in data
    assert "focus_concepts" in data

    assert isinstance(data["practice_problems"], list)
    assert isinstance(data["focus_concepts"], list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weekly_diagnostic_validation_error(api_client):
    """
    Test: POST /api/v1/workflows/weekly-diagnostic - 유효성 검증 실패

    잘못된 요청 데이터에 대한 에러 처리 테스트
    """
    # Given: student_id 없음
    request_data = {
        "curriculum_path": "중학수학.2학년.1학기"
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/weekly-diagnostic",
        json=request_data
    )

    # Then
    assert response.status_code == 422  # Validation Error


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_review_validation_error(api_client):
    """
    Test: POST /api/v1/workflows/error-review - 유효성 검증 실패
    """
    # Given: 필수 필드 누락
    request_data = {
        "student_id": "student_001"
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/error-review",
        json=request_data
    )

    # Then
    assert response.status_code == 422  # Validation Error


@pytest.mark.integration
@pytest.mark.asyncio
async def test_learning_path_validation_error(api_client):
    """
    Test: POST /api/v1/workflows/learning-path - 유효성 검증 실패
    """
    # Given: target_concept 없음
    request_data = {
        "student_id": "student_001",
        "days": 14
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/learning-path",
        json=request_data
    )

    # Then
    assert response.status_code == 422  # Validation Error


@pytest.mark.integration
@pytest.mark.asyncio
async def test_exam_prep_validation_error(api_client):
    """
    Test: POST /api/v1/workflows/exam-prep - 유효성 검증 실패
    """
    # Given: exam_date 없음
    request_data = {
        "student_id": "student_001",
        "school_id": "서울고등학교"
    }

    # When
    response = await api_client.post(
        "/api/v1/workflows/exam-prep",
        json=request_data
    )

    # Then
    assert response.status_code == 422  # Validation Error
