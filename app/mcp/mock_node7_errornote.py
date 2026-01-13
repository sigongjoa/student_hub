"""
Mock Node 7 (Error Note) MCP Server

오답노트 및 Anki 스케줄링 Mock 구현
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import uuid


class MockNode7ErrorNote:
    """Mock Error Note MCP Server - 오답노트 및 Anki 스케줄링"""

    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []
        # Mock 오답노트 데이터
        self.error_notes: Dict[str, Dict[str, Any]] = {}

    async def create_error_note(
        self,
        student_id: str,
        question_id: str,
        student_answer: str,
        correct_answer: str,
        misconception: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        오답노트 생성

        Args:
            student_id: 학생 ID
            question_id: 문제 ID
            student_answer: 학생의 답안
            correct_answer: 정답
            misconception: 오개념 (선택사항)

        Returns:
            생성된 오답노트 정보
        """
        self.call_history.append({
            "method": "create_error_note",
            "student_id": student_id,
            "question_id": question_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # 오답노트 ID 생성
        error_note_id = f"en_{uuid.uuid4().hex[:16]}"

        # Mock 오답 분석
        analysis = {
            "misconception": misconception or "개념 이해 부족",
            "root_cause": random.choice([
                "기본 개념 미숙지",
                "문제 해석 오류",
                "계산 실수",
                "공식 적용 오류"
            ]),
            "related_concepts": ["도함수", "극한", "미분"]
        }

        error_note = {
            "id": error_note_id,
            "student_id": student_id,
            "question_id": question_id,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "analysis": analysis,
            "created_at": datetime.utcnow().isoformat(),
            "anki_data": {
                "ease_factor": 2.5,
                "interval_days": 1,
                "next_review": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
        }

        self.error_notes[error_note_id] = error_note

        return error_note

    async def get_error_note(self, error_note_id: str) -> Optional[Dict[str, Any]]:
        """
        오답노트 조회

        Args:
            error_note_id: 오답노트 ID

        Returns:
            오답노트 정보 또는 None
        """
        self.call_history.append({
            "method": "get_error_note",
            "error_note_id": error_note_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        return self.error_notes.get(error_note_id)

    async def list_error_notes_by_student(
        self,
        student_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        학생의 오답노트 목록 조회

        Args:
            student_id: 학생 ID
            limit: 최대 개수

        Returns:
            오답노트 리스트
        """
        self.call_history.append({
            "method": "list_error_notes_by_student",
            "student_id": student_id,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        })

        # 학생의 오답노트 필터링
        notes = [
            note for note in self.error_notes.values()
            if note["student_id"] == student_id
        ]

        return notes[:limit]

    async def calculate_anki_schedule(
        self,
        error_note_id: str,
        quality: int
    ) -> Dict[str, Any]:
        """
        Anki 복습 스케줄 계산

        Args:
            error_note_id: 오답노트 ID
            quality: 복습 품질 (0-5, SM-2 알고리즘)

        Returns:
            업데이트된 Anki 스케줄 정보
        """
        self.call_history.append({
            "method": "calculate_anki_schedule",
            "error_note_id": error_note_id,
            "quality": quality,
            "timestamp": datetime.utcnow().isoformat()
        })

        error_note = self.error_notes.get(error_note_id)
        if not error_note:
            return {
                "error": "Error note not found",
                "error_note_id": error_note_id
            }

        # SM-2 알고리즘 간소화 버전
        anki_data = error_note["anki_data"]
        ease_factor = anki_data["ease_factor"]
        interval = anki_data["interval_days"]

        # quality < 3이면 다시 처음부터
        if quality < 3:
            new_interval = 1
            new_ease_factor = max(1.3, ease_factor - 0.2)
        else:
            # quality >= 3이면 간격 증가
            if interval == 1:
                new_interval = 6
            else:
                new_interval = int(interval * ease_factor)

            # ease_factor 조정
            new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            new_ease_factor = max(1.3, new_ease_factor)

        next_review = datetime.utcnow() + timedelta(days=new_interval)

        # 업데이트
        error_note["anki_data"] = {
            "ease_factor": round(new_ease_factor, 2),
            "interval_days": new_interval,
            "next_review": next_review.isoformat(),
            "last_review": datetime.utcnow().isoformat(),
            "review_count": anki_data.get("review_count", 0) + 1
        }

        return error_note["anki_data"]

    async def get_due_reviews(
        self,
        student_id: str,
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        복습 예정인 오답노트 조회

        Args:
            student_id: 학생 ID
            date: 기준 날짜 (ISO format, 없으면 오늘)

        Returns:
            복습 예정 오답노트 리스트
        """
        self.call_history.append({
            "method": "get_due_reviews",
            "student_id": student_id,
            "date": date,
            "timestamp": datetime.utcnow().isoformat()
        })

        target_date = datetime.fromisoformat(date) if date else datetime.utcnow()

        # 복습 예정인 노트 필터링
        due_notes = []
        for note in self.error_notes.values():
            if note["student_id"] != student_id:
                continue

            next_review = datetime.fromisoformat(note["anki_data"]["next_review"])
            if next_review <= target_date:
                due_notes.append(note)

        return due_notes

    async def update_error_note(
        self,
        error_note_id: str,
        analysis: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        오답노트 업데이트

        Args:
            error_note_id: 오답노트 ID
            analysis: 업데이트할 분석 정보
            tags: 태그

        Returns:
            업데이트된 오답노트 또는 None
        """
        self.call_history.append({
            "method": "update_error_note",
            "error_note_id": error_note_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        error_note = self.error_notes.get(error_note_id)
        if not error_note:
            return None

        if analysis:
            error_note["analysis"].update(analysis)

        if tags:
            error_note["tags"] = tags

        error_note["updated_at"] = datetime.utcnow().isoformat()

        return error_note

    async def delete_error_note(self, error_note_id: str) -> bool:
        """
        오답노트 삭제

        Args:
            error_note_id: 오답노트 ID

        Returns:
            삭제 성공 여부
        """
        self.call_history.append({
            "method": "delete_error_note",
            "error_note_id": error_note_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        if error_note_id in self.error_notes:
            del self.error_notes[error_note_id]
            return True

        return False

    def get_call_history(self) -> List[Dict[str, Any]]:
        """호출 이력 반환"""
        return self.call_history

    def clear_history(self):
        """호출 이력 초기화"""
        self.call_history = []

    def reset(self):
        """전체 데이터 초기화"""
        self.call_history = []
        self.error_notes = {}
