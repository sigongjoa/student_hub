"""
BKT (Bayesian Knowledge Tracing) Algorithm

학생의 개념 숙련도를 베이지안 추론으로 계산하는 알고리즘

Reference:
- Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge.

BKT는 4가지 파라미터를 사용:
- p_init (L0): 초기 숙련도 확률
- p_learn (T): 학습 전이 확률 (모르는 상태 → 아는 상태)
- p_slip (S): 실수 확률 (알지만 틀릴 확률)
- p_guess (G): 추측 확률 (모르지만 맞출 확률)

업데이트 수식:
1. 정답 관측 시:
   P(L_t | correct) = P(L_t-1) * (1-S) / [P(L_t-1)*(1-S) + (1-P(L_t-1))*G]

2. 오답 관측 시:
   P(L_t | wrong) = P(L_t-1) * S / [P(L_t-1)*S + (1-P(L_t-1))*(1-G)]

3. 학습 전이:
   P(L_t) = P(L_t | evidence) + (1 - P(L_t | evidence)) * T
"""
from typing import List, Union, Dict, Any


class BayesianKnowledgeTracing:
    """
    BKT 알고리즘 구현

    Examples:
        >>> bkt = BayesianKnowledgeTracing()
        >>> attempts = [{"is_correct": True}, {"is_correct": True}, {"is_correct": False}]
        >>> mastery = bkt.calculate_mastery(attempts)
        >>> print(f"Mastery: {mastery:.2f}")
        Mastery: 0.65
    """

    def __init__(
        self,
        p_init: float = 0.1,
        p_learn: float = 0.3,
        p_slip: float = 0.1,
        p_guess: float = 0.2
    ):
        """
        BKT 초기화

        Args:
            p_init: 초기 숙련도 확률 (기본값: 0.1 = 10%)
            p_learn: 학습 전이 확률 (기본값: 0.3 = 30%)
            p_slip: 실수 확률 (기본값: 0.1 = 10%)
            p_guess: 추측 확률 (기본값: 0.2 = 20%)

        Raises:
            ValueError: 파라미터가 [0, 1] 범위를 벗어난 경우
        """
        self._validate_probability(p_init, "p_init")
        self._validate_probability(p_learn, "p_learn")
        self._validate_probability(p_slip, "p_slip")
        self._validate_probability(p_guess, "p_guess")

        self.p_init = p_init
        self.p_learn = p_learn
        self.p_slip = p_slip
        self.p_guess = p_guess

    @staticmethod
    def _validate_probability(value: float, name: str) -> None:
        """
        확률 값 검증

        Args:
            value: 검증할 값
            name: 파라미터 이름

        Raises:
            ValueError: 값이 [0, 1] 범위를 벗어난 경우
        """
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1, got {value}")

    def calculate_mastery(
        self,
        attempts: List[Union[Dict[str, Any], Any]]
    ) -> float:
        """
        학생의 현재 숙련도 계산

        Args:
            attempts: 학생의 시도 기록 리스트
                      각 시도는 dict({"is_correct": bool})
                      또는 is_correct 속성을 가진 객체

        Returns:
            현재 숙련도 확률 (0.0 ~ 1.0)

        Examples:
            >>> bkt = BayesianKnowledgeTracing()
            >>> attempts = [
            ...     {"is_correct": True},
            ...     {"is_correct": True},
            ...     {"is_correct": False}
            ... ]
            >>> mastery = bkt.calculate_mastery(attempts)
            >>> assert 0.0 <= mastery <= 1.0
        """
        # 시도 기록이 없으면 초기 숙련도 반환
        if not attempts:
            return self.p_init

        # 초기 숙련도로 시작
        p_mastery = self.p_init

        # 각 시도에 대해 베이지안 업데이트
        for attempt in attempts:
            # dict 또는 객체 모두 지원
            if isinstance(attempt, dict):
                is_correct = attempt["is_correct"]
            else:
                is_correct = attempt.is_correct

            # 관측 결과에 따라 숙련도 업데이트
            if is_correct:
                # 정답: P(L | correct) 계산
                p_mastery = self._update_correct(p_mastery)
                # 학습 전이는 정답 후에만 적용 (실제 학습이 일어날 때)
                p_mastery = p_mastery + (1 - p_mastery) * self.p_learn
            else:
                # 오답: P(L | wrong) 계산
                p_mastery = self._update_wrong(p_mastery)
                # 오답 후에는 학습 전이 없음

            # 확률 범위 보정 (수치 오차 방지)
            p_mastery = max(0.0, min(1.0, p_mastery))

        return p_mastery

    def _update_correct(self, p_mastery: float) -> float:
        """
        정답 관측 시 숙련도 업데이트

        Formula:
            P(L | correct) = P(L) * (1-S) / [P(L)*(1-S) + (1-P(L))*G]

        Args:
            p_mastery: 현재 숙련도 확률

        Returns:
            업데이트된 숙련도 확률
        """
        numerator = p_mastery * (1 - self.p_slip)
        denominator = (
            p_mastery * (1 - self.p_slip) +
            (1 - p_mastery) * self.p_guess
        )

        # 분모가 0인 경우 방지 (수치 안정성)
        if denominator == 0:
            return p_mastery

        return numerator / denominator

    def _update_wrong(self, p_mastery: float) -> float:
        """
        오답 관측 시 숙련도 업데이트

        Formula:
            P(L | wrong) = P(L) * S / [P(L)*S + (1-P(L))*(1-G)]

        Args:
            p_mastery: 현재 숙련도 확률

        Returns:
            업데이트된 숙련도 확률
        """
        numerator = p_mastery * self.p_slip
        denominator = (
            p_mastery * self.p_slip +
            (1 - p_mastery) * (1 - self.p_guess)
        )

        # 분모가 0인 경우 방지 (수치 안정성)
        if denominator == 0:
            return p_mastery

        return numerator / denominator

    def __repr__(self) -> str:
        """문자열 표현"""
        return (
            f"BayesianKnowledgeTracing("
            f"p_init={self.p_init}, "
            f"p_learn={self.p_learn}, "
            f"p_slip={self.p_slip}, "
            f"p_guess={self.p_guess})"
        )
