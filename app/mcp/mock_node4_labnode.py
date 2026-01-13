"""
Mock Node 4 (Lab Node) MCP Server

학생 활동 데이터 및 학습 분석 Mock 구현
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random


class MockNode4LabNode:
    """Mock Lab Node MCP Server - 학생 활동 및 학습 분석"""

    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []
        # Mock 학생 활동 데이터
        self.student_activity_data: Dict[str, List[Dict[str, Any]]] = {}

    async def get_recent_concepts(
        self,
        student_id: str,
        days: int = 7,
        curriculum_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        최근 학습한 개념 조회

        Args:
            student_id: 학생 ID
            days: 조회 기간 (일)
            curriculum_path: 커리큘럼 경로 (필터용, optional)

        Returns:
            개념 리스트를 포함한 dict
        """
        self.call_history.append({
            "method": "get_recent_concepts",
            "student_id": student_id,
            "days": days,
            "curriculum_path": curriculum_path,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 데이터: 최근 학습 개념
        concepts = ["도함수", "적분", "극한", "미분"] if random.random() > 0.3 else ["삼각함수", "이차함수"]
        return {
            "concepts": concepts,
            "student_id": student_id,
            "period_days": days
        }

    async def get_concept_heatmap(
        self,
        student_id: str,
        curriculum_path: Optional[str] = None
    ) -> Dict[str, float]:
        """
        개념별 숙련도 히트맵 조회

        Args:
            student_id: 학생 ID
            curriculum_path: 커리큘럼 경로 (필터용)

        Returns:
            개념별 정확도 딕셔너리
        """
        self.call_history.append({
            "method": "get_concept_heatmap",
            "student_id": student_id,
            "curriculum_path": curriculum_path,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 히트맵 데이터
        return {
            "극한": round(random.uniform(0.3, 0.6), 2),
            "도함수": round(random.uniform(0.4, 0.7), 2),
            "적분": round(random.uniform(0.2, 0.5), 2),
            "미분": round(random.uniform(0.5, 0.8), 2),
            "삼각함수": round(random.uniform(0.6, 0.9), 2),
            "이차함수": round(random.uniform(0.5, 0.8), 2)
        }

    async def get_weak_concepts(
        self,
        student_id: str,
        threshold: float = 0.6,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        약점 개념 조회

        Args:
            student_id: 학생 ID
            threshold: 약점 판단 임계값
            limit: 최대 개수

        Returns:
            약점 개념 리스트
        """
        self.call_history.append({
            "method": "get_weak_concepts",
            "student_id": student_id,
            "threshold": threshold,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 약점 개념
        weak_concepts = [
            {"concept": "적분", "accuracy": 0.35, "attempts": 10},
            {"concept": "극한", "accuracy": 0.45, "attempts": 15},
            {"concept": "도함수", "accuracy": 0.55, "attempts": 20}
        ]

        return weak_concepts[:limit]

    async def get_student_activity_summary(
        self,
        student_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        학생 활동 요약 조회

        Args:
            student_id: 학생 ID
            start_date: 시작 날짜 (ISO format)
            end_date: 종료 날짜 (ISO format)

        Returns:
            활동 요약 정보
        """
        self.call_history.append({
            "method": "get_student_activity_summary",
            "student_id": student_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 활동 요약
        total_attempts = random.randint(50, 200)
        accuracy = round(random.uniform(0.5, 0.85), 2)
        total_correct = int(total_attempts * accuracy)

        return {
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "overall_accuracy": accuracy,
            "active_days": random.randint(10, 30),
            "total_study_minutes": random.randint(300, 1500),
            "average_session_minutes": random.randint(20, 60),
            "concepts_studied": random.randint(5, 15)
        }

    async def get_class_analytics(
        self,
        class_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        클래스 분석 데이터 조회

        Args:
            class_id: 클래스 ID
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            클래스 분석 정보
        """
        self.call_history.append({
            "method": "get_class_analytics",
            "class_id": class_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 클래스 분석
        total = random.randint(20, 40)
        active = random.randint(15, min(35, total))  # active는 total보다 작거나 같아야 함
        return {
            "total_students": total,
            "active_students": active,
            "average_accuracy": round(random.uniform(0.55, 0.75), 2),
            "at_risk_students": random.randint(2, min(8, total)),  # at_risk도 total보다 작아야 함
            "common_weak_concepts": [
                {"concept": "적분", "struggling_count": random.randint(5, 15)},
                {"concept": "극한", "struggling_count": random.randint(3, 12)}
            ],
            "top_performers": random.randint(3, 10)
        }

    async def get_learning_timeline(
        self,
        student_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        학생의 학습 타임라인 조회

        Args:
            student_id: 학생 ID
            days: 조회 기간 (일)

        Returns:
            학습 타임라인 (날짜별 활동)
        """
        self.call_history.append({
            "method": "get_learning_timeline",
            "student_id": student_id,
            "days": days,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Mock 타임라인 데이터
        timeline = []
        for i in range(min(days, 10)):  # 최근 10일만 생성
            date = (datetime.utcnow() - timedelta(days=i)).date().isoformat()
            timeline.append({
                "date": date,
                "attempts": random.randint(0, 20),
                "correct": random.randint(0, 15),
                "study_minutes": random.randint(0, 90),
                "concepts_studied": ["도함수", "적분"] if random.random() > 0.5 else ["극한"]
            })

        return timeline

    def get_call_history(self) -> List[Dict[str, Any]]:
        """호출 이력 반환"""
        return self.call_history

    def clear_history(self):
        """호출 이력 초기화"""
        self.call_history = []

    def reset(self):
        """전체 데이터 초기화"""
        self.call_history = []
        self.student_activity_data = {}
