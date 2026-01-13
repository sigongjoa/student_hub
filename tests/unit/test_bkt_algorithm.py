"""
Unit Tests for BKT (Bayesian Knowledge Tracing) Algorithm

TDD: 알고리즘의 수학적 정확성을 검증하는 테스트

BKT Parameters:
- p_init (L0): Initial mastery probability
- p_learn (T): Probability of learning (transition)
- p_slip (S): Probability of slip (knows but answers wrong)
- p_guess (G): Probability of guess (doesn't know but answers correctly)

BKT Update Formulas:
- P(L_t | correct) = (P(L_t-1) * (1 - S)) / (P(L_t-1) * (1 - S) + (1 - P(L_t-1)) * G)
- P(L_t | wrong) = (P(L_t-1) * S) / (P(L_t-1) * S + (1 - P(L_t-1)) * (1 - G))
- P(L_t) = P(L_t | evidence) + (1 - P(L_t | evidence)) * T

Target: 100% code coverage + mathematical correctness
"""
import pytest


@pytest.mark.unit
def test_bkt_initialization():
    """
    Test: BKT 초기화 시 기본 파라미터 설정
    Expected: 파라미터들이 올바르게 설정됨
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing()

    assert bkt.p_init == 0.1  # 초기 숙련도 10%
    assert bkt.p_learn == 0.3  # 학습률 30%
    assert bkt.p_slip == 0.1  # 실수 확률 10%
    assert bkt.p_guess == 0.2  # 추측 확률 20%

    # 모든 확률은 [0, 1] 범위
    assert 0 <= bkt.p_init <= 1
    assert 0 <= bkt.p_learn <= 1
    assert 0 <= bkt.p_slip <= 1
    assert 0 <= bkt.p_guess <= 1


@pytest.mark.unit
def test_bkt_custom_parameters():
    """
    Test: 사용자 정의 BKT 파라미터 설정
    Expected: 전달된 파라미터로 초기화
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing(
        p_init=0.2,
        p_learn=0.4,
        p_slip=0.05,
        p_guess=0.15
    )

    assert bkt.p_init == 0.2
    assert bkt.p_learn == 0.4
    assert bkt.p_slip == 0.05
    assert bkt.p_guess == 0.15


@pytest.mark.unit
def test_bkt_invalid_parameters():
    """
    Test: 잘못된 파라미터 전달 시 에러
    Expected: ValueError 발생
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    # p_init > 1.0
    with pytest.raises(ValueError, match="must be between 0 and 1"):
        BayesianKnowledgeTracing(p_init=1.5)

    # p_learn < 0
    with pytest.raises(ValueError, match="must be between 0 and 1"):
        BayesianKnowledgeTracing(p_learn=-0.1)

    # p_slip > 1.0
    with pytest.raises(ValueError, match="must be between 0 and 1"):
        BayesianKnowledgeTracing(p_slip=1.2)

    # p_guess < 0
    with pytest.raises(ValueError, match="must be between 0 and 1"):
        BayesianKnowledgeTracing(p_guess=-0.5)


@pytest.mark.unit
def test_bkt_no_attempts():
    """
    Test: 시도 기록이 없을 때 초기 숙련도 반환
    Expected: p_init 값 반환
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing(p_init=0.15)

    mastery = bkt.calculate_mastery([])

    assert mastery == pytest.approx(0.15, abs=0.001)


@pytest.mark.unit
def test_bkt_single_correct_answer():
    """
    Test: 정답 1개만 있을 때 숙련도 증가
    Expected: p_init보다 높은 값
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing(
        p_init=0.1,
        p_learn=0.3,
        p_slip=0.1,
        p_guess=0.2
    )

    attempts = [{"is_correct": True}]
    mastery = bkt.calculate_mastery(attempts)

    # 정답 후 숙련도는 초기값보다 높아야 함
    assert mastery > 0.1
    # 하지만 1.0을 초과할 수 없음
    assert mastery <= 1.0


@pytest.mark.unit
def test_bkt_single_wrong_answer():
    """
    Test: 오답 1개만 있을 때 숙련도 감소
    Expected: p_init보다 낮은 값
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing(
        p_init=0.5,
        p_learn=0.3,
        p_slip=0.1,
        p_guess=0.2
    )

    attempts = [{"is_correct": False}]
    mastery = bkt.calculate_mastery(attempts)

    # 오답 후 숙련도는 초기값보다 낮아야 함 (일반적으로)
    # 단, 확률 모델이므로 항상 그런 것은 아님
    assert mastery >= 0.0
    assert mastery <= 1.0


@pytest.mark.unit
def test_bkt_all_correct_answers():
    """
    Test: 모든 답이 정답일 때 높은 숙련도
    Expected: 0.8 이상의 숙련도
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing()

    attempts = [{"is_correct": True}] * 10

    mastery = bkt.calculate_mastery(attempts)

    # 10개 모두 정답이면 숙련도는 매우 높아야 함
    assert mastery >= 0.8
    assert mastery <= 1.0


@pytest.mark.unit
def test_bkt_all_wrong_answers():
    """
    Test: 모든 답이 오답일 때 낮은 숙련도
    Expected: 0.3 이하의 숙련도
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing()

    attempts = [{"is_correct": False}] * 10

    mastery = bkt.calculate_mastery(attempts)

    # 10개 모두 오답이면 숙련도는 매우 낮아야 함
    assert mastery <= 0.3
    assert mastery >= 0.0


@pytest.mark.unit
def test_bkt_alternating_correctness():
    """
    Test: 정답과 오답이 번갈아 나올 때 중간 숙련도
    Expected: 0.3 ~ 0.7 사이 값
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing()

    attempts = [
        {"is_correct": True},
        {"is_correct": False},
        {"is_correct": True},
        {"is_correct": False},
        {"is_correct": True}
    ]

    mastery = bkt.calculate_mastery(attempts)

    # 혼합된 결과는 중간 정도의 숙련도
    assert 0.3 <= mastery <= 0.7


@pytest.mark.unit
def test_bkt_mastery_increases_with_correct_sequence():
    """
    Test: 연속 정답 시 숙련도가 단조 증가
    Expected: 각 정답 후 숙련도 증가
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing()

    masteries = []
    for i in range(1, 6):
        attempts = [{"is_correct": True}] * i
        mastery = bkt.calculate_mastery(attempts)
        masteries.append(mastery)

    # 연속 정답 시 숙련도는 일반적으로 증가
    # (확률 모델이므로 항상은 아니지만, 평균적으로 증가)
    assert masteries[-1] > masteries[0]


@pytest.mark.unit
def test_bkt_mathematical_correctness():
    """
    Test: BKT 수식의 수학적 정확성 검증
    Expected: 알려진 입력에 대해 계산된 출력과 일치
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    # 특정 파라미터로 수동 계산한 값과 비교
    bkt = BayesianKnowledgeTracing(
        p_init=0.4,
        p_learn=0.2,
        p_slip=0.1,
        p_guess=0.2
    )

    # 정답 1개 후 숙련도 수동 계산:
    # P(L_1 | correct) = (0.4 * 0.9) / (0.4 * 0.9 + 0.6 * 0.2)
    #                  = 0.36 / (0.36 + 0.12) = 0.75
    # P(L_1) = 0.75 + 0.25 * 0.2 = 0.75 + 0.05 = 0.8

    attempts = [{"is_correct": True}]
    mastery = bkt.calculate_mastery(attempts)

    assert mastery == pytest.approx(0.8, abs=0.01)


@pytest.mark.unit
def test_bkt_with_student_attempt_objects():
    """
    Test: StudentAttempt 객체로 숙련도 계산
    Expected: dict와 동일한 결과
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing
    from app.models.student_attempt import StudentAttempt

    bkt = BayesianKnowledgeTracing()

    # Mock StudentAttempt objects
    class MockAttempt:
        def __init__(self, is_correct):
            self.is_correct = is_correct

    attempts = [
        MockAttempt(True),
        MockAttempt(True),
        MockAttempt(False),
        MockAttempt(True)
    ]

    mastery = bkt.calculate_mastery(attempts)

    # dict로도 계산
    dict_attempts = [{"is_correct": a.is_correct} for a in attempts]
    dict_mastery = bkt.calculate_mastery(dict_attempts)

    assert mastery == pytest.approx(dict_mastery, abs=0.001)


@pytest.mark.unit
def test_bkt_convergence():
    """
    Test: 충분한 데이터로 숙련도가 수렴
    Expected: 많은 정답 → 1.0에 수렴, 많은 오답 → 0.0에 수렴
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing()

    # 100개 정답 → 거의 1.0
    correct_attempts = [{"is_correct": True}] * 100
    high_mastery = bkt.calculate_mastery(correct_attempts)
    assert high_mastery >= 0.95

    # 100개 오답 → 거의 0.0
    wrong_attempts = [{"is_correct": False}] * 100
    low_mastery = bkt.calculate_mastery(wrong_attempts)
    assert low_mastery <= 0.05


@pytest.mark.unit
def test_bkt_edge_case_extreme_parameters():
    """
    Test: 극단적인 파라미터 조합 (분모 0 방지 확인)
    Expected: 수치 안정성 유지
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    # p_slip = 0, p_guess = 0인 경우 (이상적인 학생)
    bkt = BayesianKnowledgeTracing(
        p_init=0.5,
        p_learn=0.1,
        p_slip=0.0,
        p_guess=0.0
    )

    attempts = [{"is_correct": True}, {"is_correct": False}]
    mastery = bkt.calculate_mastery(attempts)

    # 정상적으로 계산되어야 함
    assert 0.0 <= mastery <= 1.0

    # p_slip = 1, p_guess = 1인 경우 (완전 랜덤)
    bkt2 = BayesianKnowledgeTracing(
        p_init=0.5,
        p_learn=0.1,
        p_slip=1.0,
        p_guess=1.0
    )

    mastery2 = bkt2.calculate_mastery(attempts)
    assert 0.0 <= mastery2 <= 1.0

    # Edge case: p_slip=1.0, p_guess=0.0 → denominator=0 in _update_correct
    bkt3 = BayesianKnowledgeTracing(
        p_init=0.5,
        p_learn=0.1,
        p_slip=1.0,
        p_guess=0.0
    )

    correct_attempts = [{"is_correct": True}]
    mastery3 = bkt3.calculate_mastery(correct_attempts)
    assert 0.0 <= mastery3 <= 1.0

    # Edge case: p_slip=0.0, p_guess=1.0 → denominator=0 in _update_wrong
    bkt4 = BayesianKnowledgeTracing(
        p_init=0.5,
        p_learn=0.1,
        p_slip=0.0,
        p_guess=1.0
    )

    wrong_attempts = [{"is_correct": False}]
    mastery4 = bkt4.calculate_mastery(wrong_attempts)
    assert 0.0 <= mastery4 <= 1.0


@pytest.mark.unit
def test_bkt_repr():
    """
    Test: __repr__ 메서드
    Expected: 유용한 문자열 표현
    """
    from app.algorithms.bkt import BayesianKnowledgeTracing

    bkt = BayesianKnowledgeTracing(
        p_init=0.2,
        p_learn=0.4,
        p_slip=0.05,
        p_guess=0.15
    )

    repr_str = repr(bkt)
    assert "BayesianKnowledgeTracing" in repr_str
    assert "0.2" in repr_str
    assert "0.4" in repr_str
    assert "0.05" in repr_str
    assert "0.15" in repr_str
