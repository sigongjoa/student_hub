"""
MCP Server for Student Hub

Node 0 (Student Hub)의 기능을 MCP 프로토콜로 노출합니다.

Tools:
- calculate_mastery: 학생의 개념 숙련도 계산
- get_mastery_profile: 학생의 전체 숙련도 프로파일 조회
- identify_weak_concepts: 약점 개념 식별
- get_student_attempts: 학생의 시도 기록 조회
"""
import json
from typing import Optional
from app.services.mastery_service import MasteryService


class MCPServer:
    """Student Hub MCP Server"""

    def __init__(self, mastery_service: MasteryService):
        """
        MCP 서버 초기화

        Args:
            mastery_service: MasteryService 인스턴스
        """
        self.mastery_service = mastery_service

    async def calculate_mastery(
        self,
        student_id: str,
        concept: str
    ) -> str:
        """
        학생의 개념 숙련도 계산

        Args:
            student_id: 학생 ID
            concept: 개념명

        Returns:
            JSON 문자열
            {
                "student_id": str,
                "concept": str,
                "mastery": float
            }
        """
        mastery = await self.mastery_service.calculate_concept_mastery(
            student_id, concept
        )

        result = {
            "student_id": student_id,
            "concept": concept,
            "mastery": mastery
        }

        return json.dumps(result, ensure_ascii=False)

    async def get_mastery_profile(
        self,
        student_id: str
    ) -> str:
        """
        학생의 전체 숙련도 프로파일 조회

        Args:
            student_id: 학생 ID

        Returns:
            JSON 문자열
            {
                "student_id": str,
                "profile": {
                    "concept1": float,
                    "concept2": float,
                    ...
                }
            }
        """
        profile = await self.mastery_service.get_student_mastery_profile(
            student_id
        )

        result = {
            "student_id": student_id,
            "profile": profile
        }

        return json.dumps(result, ensure_ascii=False)

    async def identify_weak_concepts(
        self,
        student_id: str,
        threshold: float = 0.5
    ) -> str:
        """
        약점 개념 식별

        Args:
            student_id: 학생 ID
            threshold: 약점 판단 임계값

        Returns:
            JSON 문자열
            {
                "student_id": str,
                "threshold": float,
                "weak_concepts": [str, ...]
            }
        """
        weak_concepts = await self.mastery_service.identify_weak_concepts(
            student_id, threshold
        )

        result = {
            "student_id": student_id,
            "threshold": threshold,
            "weak_concepts": weak_concepts
        }

        return json.dumps(result, ensure_ascii=False)

    async def get_student_attempts(
        self,
        student_id: str,
        concept: str,
        limit: Optional[int] = None
    ) -> str:
        """
        학생의 시도 기록 조회

        Args:
            student_id: 학생 ID
            concept: 개념명
            limit: 최대 반환 개수

        Returns:
            JSON 문자열
            {
                "student_id": str,
                "concept": str,
                "attempts": [
                    {
                        "question_id": str,
                        "is_correct": bool,
                        "response_time_ms": int,
                        "attempted_at": str
                    },
                    ...
                ]
            }
        """
        # Repository에서 시도 기록 조회
        attempts = await self.mastery_service.repository.get_by_concept(
            student_id, concept
        )

        # limit 적용
        if limit is not None:
            attempts = attempts[:limit]

        # JSON 직렬화 가능한 형태로 변환
        attempts_data = [
            {
                "question_id": attempt.question_id,
                "is_correct": attempt.is_correct,
                "response_time_ms": attempt.response_time_ms,
                "attempted_at": attempt.attempted_at.isoformat()
            }
            for attempt in attempts
        ]

        result = {
            "student_id": student_id,
            "concept": concept,
            "attempts": attempts_data
        }

        return json.dumps(result, ensure_ascii=False)
