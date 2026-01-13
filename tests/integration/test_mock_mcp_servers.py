"""
Mock MCP Servers Integration Tests

Node 2 (Q-DNA), Node 4 (Lab Node), Node 7 (Error Note) Mock 서버 통합 테스트
"""
import pytest
from app.mcp.mock_node2_qdna import MockNode2QDNA
from app.mcp.mock_node4_labnode import MockNode4LabNode
from app.mcp.mock_node7_errornote import MockNode7ErrorNote


# ==================== Node 2 (Q-DNA) Tests ====================

@pytest.mark.asyncio
async def test_node2_get_student_mastery():
    """Q-DNA: 학생 숙련도 조회 테스트"""
    node2 = MockNode2QDNA()

    mastery = await node2.get_student_mastery(
        student_id="student_001",
        concepts=["도함수", "적분"]
    )

    assert "도함수" in mastery
    assert "적분" in mastery
    assert 0.0 <= mastery["도함수"] <= 1.0
    assert 0.0 <= mastery["적분"] <= 1.0

    # 호출 이력 확인
    history = node2.get_call_history()
    assert len(history) == 1
    assert history[0]["method"] == "get_student_mastery"


@pytest.mark.asyncio
async def test_node2_recommend_questions():
    """Q-DNA: 문제 추천 테스트"""
    node2 = MockNode2QDNA()

    result = await node2.recommend_questions(
        student_id="student_001",
        concept="도함수",
        difficulty="medium",
        count=5
    )

    assert isinstance(result, dict)
    assert "questions" in result
    assert result["student_id"] == "student_001"
    assert result["count"] == 5

    questions = result["questions"]
    assert len(questions) == 5
    for q in questions:
        assert "id" in q
        assert "content" in q
        assert q["difficulty"] == "medium"
        assert "도함수" in q["concepts"]


@pytest.mark.asyncio
async def test_node2_get_question_dna():
    """Q-DNA: 문제 DNA 정보 조회 테스트"""
    node2 = MockNode2QDNA()

    dna = await node2.get_question_dna("q_test_001")

    assert dna["question_id"] == "q_test_001"
    assert "difficulty" in dna
    assert "concepts" in dna
    assert "bloom_level" in dna
    assert isinstance(dna["concepts"], list)


@pytest.mark.asyncio
async def test_node2_estimate_learning_time():
    """Q-DNA: 학습 시간 추정 테스트"""
    node2 = MockNode2QDNA()

    estimate = await node2.estimate_learning_time(
        concept="적분",
        current_mastery=0.3,
        target_mastery=0.8
    )

    assert estimate["concept"] == "적분"
    assert estimate["current_mastery"] == 0.3
    assert estimate["target_mastery"] == 0.8
    assert estimate["estimated_hours"] > 0
    assert "recommended_sessions" in estimate


# ==================== Node 4 (Lab Node) Tests ====================

@pytest.mark.asyncio
async def test_node4_get_recent_concepts():
    """Lab Node: 최근 학습 개념 조회 테스트"""
    node4 = MockNode4LabNode()

    result = await node4.get_recent_concepts(
        student_id="student_001",
        days=7
    )

    assert isinstance(result, dict)
    assert "concepts" in result
    assert isinstance(result["concepts"], list)
    assert len(result["concepts"]) > 0
    assert result["student_id"] == "student_001"
    assert result["period_days"] == 7

    # 호출 이력 확인
    history = node4.get_call_history()
    assert len(history) == 1
    assert history[0]["method"] == "get_recent_concepts"


@pytest.mark.asyncio
async def test_node4_get_concept_heatmap():
    """Lab Node: 개념 히트맵 조회 테스트"""
    node4 = MockNode4LabNode()

    heatmap = await node4.get_concept_heatmap(
        student_id="student_001"
    )

    assert isinstance(heatmap, dict)
    assert len(heatmap) > 0

    for concept, accuracy in heatmap.items():
        assert 0.0 <= accuracy <= 1.0


@pytest.mark.asyncio
async def test_node4_get_weak_concepts():
    """Lab Node: 약점 개념 조회 테스트"""
    node4 = MockNode4LabNode()

    weak_concepts = await node4.get_weak_concepts(
        student_id="student_001",
        threshold=0.6,
        limit=3
    )

    assert isinstance(weak_concepts, list)
    assert len(weak_concepts) <= 3

    for concept_data in weak_concepts:
        assert "concept" in concept_data
        assert "accuracy" in concept_data
        assert "attempts" in concept_data
        assert concept_data["accuracy"] < 0.6


@pytest.mark.asyncio
async def test_node4_get_student_activity_summary():
    """Lab Node: 학생 활동 요약 조회 테스트"""
    node4 = MockNode4LabNode()

    summary = await node4.get_student_activity_summary(
        student_id="student_001"
    )

    assert "total_attempts" in summary
    assert "total_correct" in summary
    assert "overall_accuracy" in summary
    assert "active_days" in summary
    assert summary["total_attempts"] >= summary["total_correct"]


@pytest.mark.asyncio
async def test_node4_get_class_analytics():
    """Lab Node: 클래스 분석 조회 테스트"""
    node4 = MockNode4LabNode()

    analytics = await node4.get_class_analytics(
        class_id="class_001"
    )

    assert "total_students" in analytics
    assert "active_students" in analytics
    assert "average_accuracy" in analytics
    assert "at_risk_students" in analytics
    assert analytics["active_students"] <= analytics["total_students"]


# ==================== Node 7 (Error Note) Tests ====================

@pytest.mark.asyncio
async def test_node7_create_error_note():
    """Error Note: 오답노트 생성 테스트"""
    node7 = MockNode7ErrorNote()

    error_note = await node7.create_error_note(
        student_id="student_001",
        question_id="q_001",
        student_answer="잘못된 답",
        correct_answer="정답"
    )

    assert error_note["id"] is not None
    assert error_note["student_id"] == "student_001"
    assert error_note["question_id"] == "q_001"
    assert "analysis" in error_note
    assert "anki_data" in error_note

    # 호출 이력 확인
    history = node7.get_call_history()
    assert len(history) == 1
    assert history[0]["method"] == "create_error_note"


@pytest.mark.asyncio
async def test_node7_get_error_note():
    """Error Note: 오답노트 조회 테스트"""
    node7 = MockNode7ErrorNote()

    # 먼저 오답노트 생성
    created = await node7.create_error_note(
        student_id="student_001",
        question_id="q_001",
        student_answer="답1",
        correct_answer="답2"
    )

    # 조회
    found = await node7.get_error_note(created["id"])

    assert found is not None
    assert found["id"] == created["id"]
    assert found["question_id"] == "q_001"


@pytest.mark.asyncio
async def test_node7_list_error_notes_by_student():
    """Error Note: 학생별 오답노트 목록 조회 테스트"""
    node7 = MockNode7ErrorNote()

    student_id = "student_002"

    # 여러 오답노트 생성
    await node7.create_error_note(student_id, "q_001", "a1", "c1")
    await node7.create_error_note(student_id, "q_002", "a2", "c2")
    await node7.create_error_note(student_id, "q_003", "a3", "c3")

    # 목록 조회
    notes = await node7.list_error_notes_by_student(student_id, limit=10)

    assert len(notes) >= 3
    for note in notes:
        assert note["student_id"] == student_id


@pytest.mark.asyncio
async def test_node7_calculate_anki_schedule():
    """Error Note: Anki 스케줄 계산 테스트"""
    node7 = MockNode7ErrorNote()

    # 오답노트 생성
    error_note = await node7.create_error_note(
        student_id="student_001",
        question_id="q_001",
        student_answer="답1",
        correct_answer="답2"
    )

    original_interval = error_note["anki_data"]["interval_days"]

    # 복습 품질 좋음 (5점)
    anki_data = await node7.calculate_anki_schedule(
        error_note_id=error_note["id"],
        quality=5
    )

    assert anki_data["interval_days"] > original_interval
    assert "next_review" in anki_data
    assert "last_review" in anki_data


@pytest.mark.asyncio
async def test_node7_calculate_anki_schedule_poor_quality():
    """Error Note: Anki 스케줄 계산 (낮은 품질) 테스트"""
    node7 = MockNode7ErrorNote()

    # 오답노트 생성
    error_note = await node7.create_error_note(
        student_id="student_001",
        question_id="q_001",
        student_answer="답1",
        correct_answer="답2"
    )

    original_ease_factor = error_note["anki_data"]["ease_factor"]

    # 복습 품질 나쁨 (2점)
    anki_data = await node7.calculate_anki_schedule(
        error_note_id=error_note["id"],
        quality=2
    )

    # 낮은 품질이면 간격이 1일로 리셋
    assert anki_data["interval_days"] == 1
    assert anki_data["ease_factor"] <= original_ease_factor


@pytest.mark.asyncio
async def test_node7_get_due_reviews():
    """Error Note: 복습 예정 오답노트 조회 테스트"""
    node7 = MockNode7ErrorNote()

    student_id = "student_003"

    # 오답노트 생성 (복습 날짜가 자동으로 설정됨)
    await node7.create_error_note(student_id, "q_001", "a1", "c1")
    await node7.create_error_note(student_id, "q_002", "a2", "c2")

    # 복습 예정 노트 조회 (미래 날짜로 조회하면 모두 포함)
    from datetime import datetime, timedelta
    future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

    due_notes = await node7.get_due_reviews(
        student_id=student_id,
        date=future_date
    )

    assert len(due_notes) >= 2


@pytest.mark.asyncio
async def test_node7_delete_error_note():
    """Error Note: 오답노트 삭제 테스트"""
    node7 = MockNode7ErrorNote()

    # 오답노트 생성
    error_note = await node7.create_error_note(
        student_id="student_001",
        question_id="q_001",
        student_answer="답1",
        correct_answer="답2"
    )

    note_id = error_note["id"]

    # 삭제
    deleted = await node7.delete_error_note(note_id)
    assert deleted is True

    # 조회 시 없어야 함
    found = await node7.get_error_note(note_id)
    assert found is None


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_full_workflow_mock_integration():
    """전체 워크플로우 Mock 통합 테스트"""
    node2 = MockNode2QDNA()
    node4 = MockNode4LabNode()
    node7 = MockNode7ErrorNote()

    student_id = "student_integration_001"

    # 1. Lab Node에서 학생 활동 조회
    activity = await node4.get_student_activity_summary(student_id)
    assert activity["total_attempts"] > 0

    # 2. Lab Node에서 약점 개념 조회
    weak_concepts = await node4.get_weak_concepts(student_id, limit=3)
    assert len(weak_concepts) > 0

    weak_concept = weak_concepts[0]["concept"]

    # 3. Q-DNA에서 해당 개념의 숙련도 조회
    mastery = await node2.get_student_mastery(student_id, concepts=[weak_concept])
    assert weak_concept in mastery

    # 4. Q-DNA에서 문제 추천
    questions_response = await node2.recommend_questions(
        student_id=student_id,
        concept=weak_concept,
        count=5
    )
    assert isinstance(questions_response, dict)
    assert "questions" in questions_response
    questions = questions_response["questions"]
    assert len(questions) == 5

    # 5. 학생이 문제를 틀림 -> Error Note 생성
    question = questions[0]
    error_note = await node7.create_error_note(
        student_id=student_id,
        question_id=question["id"],
        student_answer="잘못된 답",
        correct_answer="정답"
    )
    assert error_note["id"] is not None

    # 6. Anki 스케줄 계산
    anki_data = await node7.calculate_anki_schedule(
        error_note_id=error_note["id"],
        quality=3  # 보통 품질
    )
    assert anki_data["interval_days"] > 0

    # 호출 이력 검증
    assert len(node2.get_call_history()) >= 2
    assert len(node4.get_call_history()) >= 2
    assert len(node7.get_call_history()) >= 2
