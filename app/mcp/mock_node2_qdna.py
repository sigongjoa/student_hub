"""
Mock Node 2 (Q-DNA) MCP Server

BKT 기반 숙련도 계산 및 문제 추천 Mock 구현
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import random


class MockNode2QDNA:
    """Mock Q-DNA MCP Server - BKT 기반 숙련도 계산"""

    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []
        # Mock 학생 데이터 저장
        self.student_mastery_data: Dict[str, Dict[str, float]] = {}

    async def get_student_mastery(
        self,
        student_id: str,
        concepts: Optional[List[str]] = None,
        skill_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        학생의 개념별 숙련도 조회 (BKT 기반)

        Args:
            student_id: 학생 ID
            concepts: 조회할 개념 리스트 (없으면 전체)
            skill_ids: concepts의 alias (호환성)

        Returns:
            개념별 숙련도 딕셔너리 (0.0 ~ 1.0)
        """
        # skill_ids가 주어지면 concepts로 사용 (호환성)
        if skill_ids and not concepts:
            concepts = skill_ids

        self.call_history.append({
            "method": "get_student_mastery",
            "student_id": student_id,
            "concepts": concepts,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 데이터: 학생별로 개념 숙련도 생성
        if student_id not in self.student_mastery_data:
            # 처음 조회 시 랜덤한 숙련도 생성
            self.student_mastery_data[student_id] = {
                "도함수": random.uniform(0.3, 0.7),
                "적분": random.uniform(0.3, 0.7),
                "극한": random.uniform(0.3, 0.7),
                "미분": random.uniform(0.3, 0.7),
                "삼각함수": random.uniform(0.5, 0.9),
                "이차함수": random.uniform(0.4, 0.8),
                "방정식": random.uniform(0.5, 0.85)
            }

        mastery = self.student_mastery_data[student_id]

        # concepts 파라미터가 있으면 필터링
        if concepts:
            return {c: mastery.get(c, 0.5) for c in concepts}

        return mastery

    async def recommend_questions(
        self,
        student_id: str,
        concept: Optional[str] = None,
        difficulty: str = "medium",
        count: int = 10,
        curriculum_path: Optional[str] = None,
        weak_concepts: Optional[List[str]] = None,
        weak_ratio: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        학생에게 맞는 문제 추천

        Args:
            student_id: 학생 ID
            concept: 개념 (선택)
            difficulty: 난이도 (easy, medium, hard)
            count: 추천할 문제 수
            curriculum_path: 커리큘럼 경로 (필터용)
            weak_concepts: 약점 개념 리스트
            weak_ratio: 약점 개념 문제 비율 (0.0 ~ 1.0)

        Returns:
            추천 문제 리스트
        """
        self.call_history.append({
            "method": "recommend_questions",
            "student_id": student_id,
            "concept": concept,
            "difficulty": difficulty,
            "count": count,
            "curriculum_path": curriculum_path,
            "weak_concepts": weak_concepts,
            "weak_ratio": weak_ratio,
            "timestamp": datetime.utcnow().isoformat()
        })

        # weak_concepts가 있으면 우선적으로 사용
        target_concepts = weak_concepts if weak_concepts else ([concept] if concept else ["도함수", "적분"])

        # Mock 문제 생성
        questions = []
        for i in range(count):
            # 약점 개념 중 랜덤 선택
            selected_concept = random.choice(target_concepts)
            questions.append({
                "id": f"q_{selected_concept}_{difficulty}_{i+1}",
                "content": f"{selected_concept} 관련 {difficulty} 난이도 문제 {i+1}",
                "difficulty": difficulty,
                "concepts": [selected_concept],
                "estimated_time_minutes": 3 if difficulty == "easy" else 5 if difficulty == "medium" else 8
            })

        return {
            "questions": questions,
            "student_id": student_id,
            "count": len(questions)
        }

    async def get_question_dna(self, question_id: str) -> Dict[str, Any]:
        """
        문제의 DNA 정보 조회 (난이도, 개념, Bloom 수준 등)

        Args:
            question_id: 문제 ID

        Returns:
            문제 DNA 정보
        """
        self.call_history.append({
            "method": "get_question_dna",
            "question_id": question_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock DNA 정보
        return {
            "question_id": question_id,
            "difficulty": random.choice(["easy", "medium", "hard"]),
            "concepts": ["도함수", "극한", "미분"] if "도함수" in question_id else ["적분", "미분"],
            "bloom_level": random.choice(["remember", "understand", "apply", "analyze"]),
            "estimated_time_minutes": random.randint(3, 10),
            "irt_difficulty": random.uniform(-2.0, 2.0)
        }

    async def estimate_learning_time(
        self,
        concept: str,
        current_mastery: float,
        target_mastery: float = 0.8
    ) -> Dict[str, Any]:
        """
        개념 학습 소요 시간 추정

        Args:
            concept: 개념
            current_mastery: 현재 숙련도 (0.0 ~ 1.0)
            target_mastery: 목표 숙련도 (0.0 ~ 1.0)

        Returns:
            학습 시간 추정 정보
        """
        self.call_history.append({
            "method": "estimate_learning_time",
            "concept": concept,
            "current_mastery": current_mastery,
            "target_mastery": target_mastery,
            "timestamp": datetime.utcnow().isoformat()
        })

        # 숙련도 차이에 기반한 학습 시간 계산
        mastery_gap = target_mastery - current_mastery
        base_hours = {"도함수": 6, "적분": 8, "극한": 4, "미분": 5}.get(concept, 5)

        estimated_hours = int(base_hours * max(0.5, mastery_gap / 0.3))

        return {
            "concept": concept,
            "current_mastery": current_mastery,
            "target_mastery": target_mastery,
            "estimated_hours": estimated_hours,
            "recommended_sessions": estimated_hours // 2,
            "daily_practice_minutes": 30
        }

    def get_call_history(self) -> List[Dict[str, Any]]:
        """호출 이력 반환"""
        return self.call_history

    def clear_history(self):
        """호출 이력 초기화"""
        self.call_history = []

    def reset(self):
        """전체 데이터 초기화"""
        self.call_history = []
        self.student_mastery_data = {}
