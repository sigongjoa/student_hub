"""
IRT (Item Response Theory) Algorithm

문제의 난이도와 학생의 능력을 동시에 추정하는 알고리즘

Reference:
- Baker, F. B. (2001). The Basics of Item Response Theory.
- Rasch, G. (1960). Probabilistic Models for Some Intelligence and Attainment Tests.

IRT Models:
- 1PL (Rasch): P(correct|θ,b) = 1 / (1 + exp(-(θ - b)))
- 2PL: P(correct|θ,a,b) = 1 / (1 + exp(-a(θ - b)))

Parameters:
- θ (theta): Student ability
- b: Item difficulty
- a: Discrimination (2PL only)

용도:
- 적응형 테스트 (Adaptive Testing)
- 문제 난이도 자동 추정
- 학생 능력 측정
"""
import math
from typing import List, Dict, Any


class ItemResponseTheory:
    """
    IRT (Item Response Theory) 알고리즘 구현

    Examples:
        >>> irt = ItemResponseTheory()
        >>> prob = irt.calculate_probability(theta=1.0, difficulty=0.0)
        >>> print(f"P(correct): {prob:.3f}")
        P(correct): 0.731
    """

    def __init__(self):
        """IRT 초기화"""
        self.max_iterations = 50
        self.tolerance = 0.001

    def calculate_probability(
        self,
        theta: float,
        difficulty: float,
        discrimination: float = 1.0
    ) -> float:
        """
        정답 확률 계산 (1PL/2PL 모델)

        Args:
            theta: 학생 능력
            difficulty: 문제 난이도
            discrimination: 변별도 (기본값: 1.0 for 1PL)

        Returns:
            정답 확률 (0.0 ~ 1.0)

        Formula:
            P(correct|θ,a,b) = 1 / (1 + exp(-a(θ - b)))
        """
        exponent = -discrimination * (theta - difficulty)

        # 수치 안정성을 위한 클리핑
        exponent = max(-20, min(20, exponent))

        probability = 1.0 / (1.0 + math.exp(exponent))

        return probability

    def estimate_ability(
        self,
        attempts: List[Dict[str, Any]],
        initial_theta: float = 0.0
    ) -> float:
        """
        학생 능력 추정 (Maximum Likelihood Estimation)

        Args:
            attempts: 시도 기록 리스트
                      각 시도는 {"difficulty": float, "is_correct": bool}
            initial_theta: 초기 능력 추정값

        Returns:
            추정된 학생 능력 (theta)

        Examples:
            >>> irt = ItemResponseTheory()
            >>> attempts = [
            ...     {"difficulty": 0.0, "is_correct": True},
            ...     {"difficulty": 1.0, "is_correct": False}
            ... ]
            >>> theta = irt.estimate_ability(attempts)
        """
        if not attempts:
            return 0.0

        theta = initial_theta

        # Newton-Raphson method
        for _ in range(self.max_iterations):
            # 1차 미분 (score)
            score = 0.0
            # 2차 미분 (information)
            information = 0.0

            for attempt in attempts:
                b = attempt["difficulty"]
                y = 1.0 if attempt["is_correct"] else 0.0

                p = self.calculate_probability(theta, b)

                # Score function: ∂L/∂θ = Σ(y - P)
                score += (y - p)

                # Information function: -∂²L/∂θ² = ΣP(1-P)
                information += p * (1 - p)

            # 수렴 확인
            if abs(score) < self.tolerance:
                break

            # Information이 0이면 업데이트 불가 (수치 안정성)
            if information < 1e-10:  # pragma: no cover - 극단적 edge case
                break

            # θ 업데이트: θ_new = θ_old + score / information
            theta += score / information

            # 극단값 방지
            theta = max(-5.0, min(5.0, theta))

        return theta

    def estimate_difficulty(
        self,
        attempts: List[Dict[str, Any]],
        initial_difficulty: float = 0.0
    ) -> float:
        """
        문제 난이도 추정

        Args:
            attempts: 시도 기록 리스트
                      각 시도는 {"theta": float, "is_correct": bool}
            initial_difficulty: 초기 난이도 추정값

        Returns:
            추정된 문제 난이도

        Examples:
            >>> irt = ItemResponseTheory()
            >>> attempts = [
            ...     {"theta": 1.0, "is_correct": True},
            ...     {"theta": 0.5, "is_correct": False}
            ... ]
            >>> difficulty = irt.estimate_difficulty(attempts)
        """
        if not attempts:
            return 0.0

        difficulty = initial_difficulty

        # Newton-Raphson method
        for _ in range(self.max_iterations):
            score = 0.0
            information = 0.0

            for attempt in attempts:
                theta = attempt["theta"]
                y = 1.0 if attempt["is_correct"] else 0.0

                p = self.calculate_probability(theta, difficulty)

                # Score function: ∂L/∂b = Σ(P - y) (부호 주의)
                score += (p - y)

                # Information function
                information += p * (1 - p)

            if abs(score) < self.tolerance:
                break

            if information < 1e-10:  # pragma: no cover - 극단적 edge case
                break

            # b 업데이트
            difficulty += score / information

            # 극단값 방지
            difficulty = max(-5.0, min(5.0, difficulty))

        return difficulty

    def calculate_information(
        self,
        theta: float,
        difficulty: float,
        discrimination: float = 1.0
    ) -> float:
        """
        Fisher 정보량 계산

        Args:
            theta: 학생 능력
            difficulty: 문제 난이도
            discrimination: 변별도

        Returns:
            정보량 (높을수록 정확한 측정)

        Formula:
            I(θ) = a² * P(θ) * (1 - P(θ))
        """
        p = self.calculate_probability(theta, difficulty, discrimination)
        information = (discrimination ** 2) * p * (1 - p)

        return information

    def select_best_question(
        self,
        student_ability: float,
        question_difficulties: List[float]
    ) -> float:
        """
        적응형 테스트를 위한 최적 문제 선택

        Args:
            student_ability: 현재 추정된 학생 능력
            question_difficulties: 사용 가능한 문제들의 난이도 리스트

        Returns:
            최대 정보량을 제공하는 문제의 난이도

        Examples:
            >>> irt = ItemResponseTheory()
            >>> best = irt.select_best_question(1.5, [0.0, 1.0, 1.5, 2.0])
            >>> print(f"Best difficulty: {best}")
            Best difficulty: 1.5
        """
        if not question_difficulties:
            return 0.0

        max_information = -1.0
        best_difficulty = question_difficulties[0]

        for difficulty in question_difficulties:
            info = self.calculate_information(student_ability, difficulty)

            if info > max_information:
                max_information = info
                best_difficulty = difficulty

        return best_difficulty

    def __repr__(self) -> str:
        """문자열 표현"""
        return (
            f"ItemResponseTheory(model='1PL', "
            f"max_iterations={self.max_iterations}, "
            f"tolerance={self.tolerance})"
        )
