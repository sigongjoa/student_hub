"""
Unit Tests for IRT (Item Response Theory) Algorithm

TDD: 문제 난이도 및 학생 능력 추정 알고리즘 검증

IRT (1-Parameter Logistic Model):
- theta (θ): 학생의 능력 (ability)
- b: 문제의 난이도 (difficulty)
- P(correct|θ,b) = 1 / (1 + exp(-(θ - b)))

IRT 용도:
- 문제 난이도 자동 추정
- 학생 능력 측정
- 적응형 테스트 (adaptive testing)

Target: 100% code coverage
"""
import pytest
import math


@pytest.mark.unit
def test_irt_probability_calculation():
    """
    Test: IRT 확률 계산
    Expected: P(correct) = 1 / (1 + exp(-(θ - b)))
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # θ = 0, b = 0 → P = 0.5
    prob = irt.calculate_probability(theta=0.0, difficulty=0.0)
    assert prob == pytest.approx(0.5, abs=0.01)

    # θ = 1, b = 0 → P > 0.5 (학생이 문제보다 능력 높음)
    prob = irt.calculate_probability(theta=1.0, difficulty=0.0)
    assert prob > 0.5
    assert prob == pytest.approx(0.731, abs=0.01)

    # θ = 0, b = 1 → P < 0.5 (문제가 학생보다 어려움)
    prob = irt.calculate_probability(theta=0.0, difficulty=1.0)
    assert prob < 0.5
    assert prob == pytest.approx(0.269, abs=0.01)


@pytest.mark.unit
def test_irt_extreme_cases():
    """
    Test: 극단적인 경우의 확률 계산
    Expected: 0 < P < 1 항상 유지
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 매우 높은 능력, 매우 쉬운 문제 → P ≈ 1
    prob = irt.calculate_probability(theta=5.0, difficulty=-5.0)
    assert prob > 0.99
    assert prob < 1.0

    # 매우 낮은 능력, 매우 어려운 문제 → P ≈ 0
    prob = irt.calculate_probability(theta=-5.0, difficulty=5.0)
    assert prob < 0.01
    assert prob > 0.0


@pytest.mark.unit
def test_estimate_student_ability():
    """
    Test: 학생 능력 추정 (Maximum Likelihood Estimation)
    Expected: 시도 기록으로부터 θ 추정
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 모든 문제를 맞춘 경우
    attempts = [
        {"difficulty": -1.0, "is_correct": True},
        {"difficulty": 0.0, "is_correct": True},
        {"difficulty": 1.0, "is_correct": True},
    ]

    theta = irt.estimate_ability(attempts)
    # 모두 맞췄으므로 능력이 높아야 함
    assert theta > 1.0

    # 모든 문제를 틀린 경우
    attempts = [
        {"difficulty": -1.0, "is_correct": False},
        {"difficulty": 0.0, "is_correct": False},
        {"difficulty": 1.0, "is_correct": False},
    ]

    theta = irt.estimate_ability(attempts)
    # 모두 틀렸으므로 능력이 낮아야 함
    assert theta < -1.0


@pytest.mark.unit
def test_estimate_ability_mixed_results():
    """
    Test: 혼합된 결과로 능력 추정
    Expected: 중간 능력 값
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 쉬운 문제는 맞추고, 어려운 문제는 틀림
    attempts = [
        {"difficulty": -1.0, "is_correct": True},   # 쉬움
        {"difficulty": -0.5, "is_correct": True},   # 쉬움
        {"difficulty": 0.5, "is_correct": False},   # 어려움
        {"difficulty": 1.0, "is_correct": False},   # 어려움
    ]

    theta = irt.estimate_ability(attempts)
    # 중간 정도 능력
    assert -1.0 < theta < 1.0


@pytest.mark.unit
def test_estimate_difficulty():
    """
    Test: 문제 난이도 추정
    Expected: 학생들의 시도 기록으로 난이도 추정
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 높은 능력 학생들이 모두 틀린 문제 → 어려운 문제
    attempts = [
        {"theta": 1.0, "is_correct": False},
        {"theta": 1.5, "is_correct": False},
        {"theta": 2.0, "is_correct": False},
    ]

    difficulty = irt.estimate_difficulty(attempts)
    assert difficulty > 2.0  # 매우 어려움

    # 낮은 능력 학생들이 모두 맞춘 문제 → 쉬운 문제
    attempts = [
        {"theta": -1.0, "is_correct": True},
        {"theta": -0.5, "is_correct": True},
        {"theta": 0.0, "is_correct": True},
    ]

    difficulty = irt.estimate_difficulty(attempts)
    assert difficulty < -1.0  # 매우 쉬움


@pytest.mark.unit
def test_estimate_difficulty_mixed():
    """
    Test: 혼합된 결과로 난이도 추정
    Expected: 중간 난이도
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 능력 0인 학생이 50% 정답 → 난이도 0
    attempts = [
        {"theta": 0.0, "is_correct": True},
        {"theta": 0.0, "is_correct": False},
        {"theta": 0.0, "is_correct": True},
        {"theta": 0.0, "is_correct": False},
    ]

    difficulty = irt.estimate_difficulty(attempts)
    assert -0.5 < difficulty < 0.5


@pytest.mark.unit
def test_estimate_ability_no_attempts():
    """
    Test: 시도 기록이 없을 때 능력 추정
    Expected: 기본값 0.0 반환
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    theta = irt.estimate_ability([])
    assert theta == pytest.approx(0.0, abs=0.01)


@pytest.mark.unit
def test_estimate_difficulty_no_attempts():
    """
    Test: 시도 기록이 없을 때 난이도 추정
    Expected: 기본값 0.0 반환
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    difficulty = irt.estimate_difficulty([])
    assert difficulty == pytest.approx(0.0, abs=0.01)


@pytest.mark.unit
def test_irt_information_function():
    """
    Test: IRT 정보 함수 (Information Function)
    Expected: I(θ) = P(θ) * (1 - P(θ))
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # θ = b일 때 정보량이 최대 (0.25)
    info = irt.calculate_information(theta=0.0, difficulty=0.0)
    assert info == pytest.approx(0.25, abs=0.01)

    # θ와 b가 크게 다를 때 정보량이 낮음
    info = irt.calculate_information(theta=5.0, difficulty=0.0)
    assert info < 0.1


@pytest.mark.unit
def test_irt_with_discrimination():
    """
    Test: 변별도(discrimination) 파라미터 포함 (2PL 모델)
    Expected: P = 1 / (1 + exp(-a(θ - b)))
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # a = 1.0 (기본값)
    prob1 = irt.calculate_probability(theta=1.0, difficulty=0.0, discrimination=1.0)

    # a = 2.0 (높은 변별도 → 더 가파른 곡선)
    prob2 = irt.calculate_probability(theta=1.0, difficulty=0.0, discrimination=2.0)

    # 변별도가 높으면 확률 차이가 더 크게 나타남
    assert prob2 > prob1


@pytest.mark.unit
def test_adaptive_question_selection():
    """
    Test: 적응형 문제 선택
    Expected: 학생의 능력에 가장 적합한 난이도 선택
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    student_ability = 1.5
    question_difficulties = [-1.0, 0.0, 1.0, 1.5, 2.0, 3.0]

    # 학생 능력과 가장 가까운 난이도 선택 (최대 정보량)
    best_difficulty = irt.select_best_question(student_ability, question_difficulties)

    # 1.5에 가장 가까운 난이도 선택되어야 함
    assert best_difficulty == pytest.approx(1.5, abs=0.1)


@pytest.mark.unit
def test_irt_convergence():
    """
    Test: 추정 알고리즘의 수렴성
    Expected: 반복 계산이 안정적으로 수렴
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 일관된 패턴의 시도 기록
    attempts = [
        {"difficulty": 0.0, "is_correct": True},
        {"difficulty": 0.5, "is_correct": True},
        {"difficulty": 1.0, "is_correct": False},
        {"difficulty": 1.5, "is_correct": False},
    ]

    # 여러 번 추정해도 일관된 결과
    theta1 = irt.estimate_ability(attempts)
    theta2 = irt.estimate_ability(attempts)

    assert theta1 == pytest.approx(theta2, abs=0.001)


@pytest.mark.unit
def test_irt_repr():
    """
    Test: __repr__ 메서드
    Expected: 유용한 문자열 표현
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    repr_str = repr(irt)
    assert "ItemResponseTheory" in repr_str
    assert "1PL" in repr_str or "IRT" in repr_str


@pytest.mark.unit
def test_estimate_ability_low_information():
    """
    Test: 정보량이 매우 낮을 때 능력 추정
    Expected: 안정적으로 처리 (information < 1e-10)
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 극단적인 초기값과 극단적인 시도로 정보량을 0에 가깝게 만듦
    # theta가 매우 높고 모든 문제를 맞춘 경우 → P ≈ 1 → information ≈ 0
    attempts = [
        {"difficulty": -5.0, "is_correct": True},
        {"difficulty": -5.0, "is_correct": True},
        {"difficulty": -5.0, "is_correct": True},
    ]

    # 매우 높은 초기값으로 시작
    theta = irt.estimate_ability(attempts, initial_theta=4.9)
    # 안정적으로 처리되어야 함
    assert -5.0 <= theta <= 5.0


@pytest.mark.unit
def test_estimate_difficulty_low_information():
    """
    Test: 정보량이 매우 낮을 때 난이도 추정
    Expected: 안정적으로 처리
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    # 극단적으로 높은 능력 학생들이 모두 맞춤 → P ≈ 1 → information ≈ 0
    attempts = [
        {"theta": 5.0, "is_correct": True},
        {"theta": 5.0, "is_correct": True},
        {"theta": 5.0, "is_correct": True},
    ]

    # 매우 낮은 초기 난이도로 시작
    difficulty = irt.estimate_difficulty(attempts, initial_difficulty=-4.9)
    # 안정적으로 처리되어야 함
    assert -5.0 <= difficulty <= 5.0


@pytest.mark.unit
def test_select_best_question_empty_list():
    """
    Test: 빈 문제 리스트에서 선택
    Expected: 기본값 0.0 반환
    """
    from app.algorithms.irt import ItemResponseTheory

    irt = ItemResponseTheory()

    best = irt.select_best_question(1.0, [])
    assert best == 0.0
