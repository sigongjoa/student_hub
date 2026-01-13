"""
Mastery Calculation Service

학생의 개념별 숙련도를 계산하는 서비스

책임:
- StudentAttemptRepository와 BKT 알고리즘 통합
- 개념별 숙련도 계산
- 약점 개념 식별
- 학생 숙련도 프로파일 생성
"""
from typing import List, Dict
from app.repositories.student_attempt_repository import StudentAttemptRepository
from app.algorithms.bkt import BayesianKnowledgeTracing


class MasteryService:
    """학생 숙련도 계산 서비스"""

    def __init__(
        self,
        repository: StudentAttemptRepository,
        bkt_algorithm: BayesianKnowledgeTracing
    ):
        """
        서비스 초기화

        Args:
            repository: StudentAttemptRepository 인스턴스
            bkt_algorithm: BayesianKnowledgeTracing 인스턴스
        """
        self.repository = repository
        self.bkt = bkt_algorithm

    async def calculate_concept_mastery(
        self,
        student_id: str,
        concept: str
    ) -> float:
        """
        학생의 특정 개념 숙련도 계산

        Args:
            student_id: 학생 ID
            concept: 개념명

        Returns:
            숙련도 확률 (0.0 ~ 1.0)

        Examples:
            >>> service = MasteryService(repo, bkt)
            >>> mastery = await service.calculate_concept_mastery("student_1", "이차방정식")
            >>> print(f"Mastery: {mastery:.2f}")
            Mastery: 0.75
        """
        # Repository에서 학습 데이터 조회
        attempts_data = await self.repository.get_student_mastery_data(
            student_id, concept
        )

        # BKT로 숙련도 계산
        mastery = self.bkt.calculate_mastery(attempts_data)

        return mastery

    async def calculate_multiple_concepts_mastery(
        self,
        student_id: str,
        concepts: List[str]
    ) -> Dict[str, float]:
        """
        여러 개념에 대한 숙련도 계산

        Args:
            student_id: 학생 ID
            concepts: 개념 리스트

        Returns:
            {개념: 숙련도} 딕셔너리

        Examples:
            >>> concepts = ["이차방정식", "삼각함수", "미분"]
            >>> mastery_map = await service.calculate_multiple_concepts_mastery("student_1", concepts)
            >>> print(mastery_map)
            {'이차방정식': 0.75, '삼각함수': 0.45, '미분': 0.82}
        """
        mastery_map = {}

        for concept in concepts:
            mastery = await self.calculate_concept_mastery(student_id, concept)
            mastery_map[concept] = mastery

        return mastery_map

    async def get_student_mastery_profile(
        self,
        student_id: str
    ) -> Dict[str, float]:
        """
        학생이 학습한 모든 개념의 숙련도 프로파일 조회

        Args:
            student_id: 학생 ID

        Returns:
            {개념: 숙련도} 딕셔너리

        Examples:
            >>> profile = await service.get_student_mastery_profile("student_1")
            >>> print(f"Total concepts: {len(profile)}")
            Total concepts: 15
        """
        # 학생의 모든 시도 기록 조회
        all_attempts = await self.repository.get_by_student(student_id)

        # 유니크한 개념 추출
        unique_concepts = list(set(attempt.concept for attempt in all_attempts))

        # 각 개념별 숙련도 계산
        profile = await self.calculate_multiple_concepts_mastery(
            student_id, unique_concepts
        )

        return profile

    async def identify_weak_concepts(
        self,
        student_id: str,
        threshold: float = 0.5
    ) -> List[str]:
        """
        약한 개념 식별

        Args:
            student_id: 학생 ID
            threshold: 약점 판단 임계값 (기본값: 0.5)

        Returns:
            약점 개념 리스트

        Examples:
            >>> weak_concepts = await service.identify_weak_concepts("student_1", threshold=0.6)
            >>> print(f"Weak concepts: {weak_concepts}")
            Weak concepts: ['이차부등식', '삼각함수']
        """
        # 전체 숙련도 프로파일 조회
        profile = await self.get_student_mastery_profile(student_id)

        # 임계값 이하의 개념 필터링
        weak_concepts = [
            concept for concept, mastery in profile.items()
            if mastery < threshold
        ]

        return weak_concepts

    async def get_concept_accuracy(
        self,
        student_id: str,
        concept: str
    ) -> float:
        """
        개념별 정답률 조회

        Args:
            student_id: 학생 ID
            concept: 개념명

        Returns:
            정답률 (0.0 ~ 1.0)

        Examples:
            >>> accuracy = await service.get_concept_accuracy("student_1", "이차방정식")
            >>> print(f"Accuracy: {accuracy:.1%}")
            Accuracy: 75.0%
        """
        accuracy = await self.repository.calculate_concept_accuracy(
            student_id, concept
        )

        return accuracy
