"""
Student Repository Tests (TDD - RED Phase)

StudentRepository CRUD 및 쿼리 테스트
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.student_repository import StudentRepository
from app.models.student import Student


@pytest.mark.asyncio
async def test_create_student(db_session: AsyncSession):
    """학생 생성 테스트"""
    repo = StudentRepository(db_session)

    student = await repo.create(
        name="김철수",
        grade=10,
        school_id="school_001"
    )

    assert student.id is not None
    assert student.name == "김철수"
    assert student.grade == 10
    assert student.school_id == "school_001"
    assert student.created_at is not None
    assert student.updated_at is not None


@pytest.mark.asyncio
async def test_get_student_by_id(db_session: AsyncSession):
    """ID로 학생 조회 테스트"""
    repo = StudentRepository(db_session)

    # Given: 학생 생성
    created = await repo.create(
        name="이영희",
        grade=11,
        school_id="school_002"
    )

    # When: ID로 조회
    found = await repo.get_by_id(created.id)

    # Then
    assert found is not None
    assert found.id == created.id
    assert found.name == "이영희"
    assert found.grade == 11


@pytest.mark.asyncio
async def test_get_student_by_id_not_found(db_session: AsyncSession):
    """존재하지 않는 학생 조회 테스트"""
    repo = StudentRepository(db_session)

    # When: 존재하지 않는 ID 조회
    found = await repo.get_by_id("nonexistent_id")

    # Then: None 반환
    assert found is None


@pytest.mark.asyncio
async def test_list_students_basic(db_session: AsyncSession):
    """학생 목록 조회 테스트 (기본)"""
    repo = StudentRepository(db_session)

    # Given: 3명의 학생 생성
    await repo.create(name="학생1", grade=10, school_id="school_001")
    await repo.create(name="학생2", grade=11, school_id="school_001")
    await repo.create(name="학생3", grade=12, school_id="school_001")

    # When: 전체 조회
    students = await repo.list_all()

    # Then
    assert len(students) >= 3
    names = [s.name for s in students]
    assert "학생1" in names
    assert "학생2" in names
    assert "학생3" in names


@pytest.mark.asyncio
async def test_list_students_with_pagination(db_session: AsyncSession):
    """학생 목록 조회 테스트 (페이지네이션)"""
    repo = StudentRepository(db_session)

    # Given: 5명의 학생 생성
    for i in range(5):
        await repo.create(
            name=f"페이지학생{i+1}",
            grade=10,
            school_id="school_page"
        )

    # When: 페이지 1 (limit=2)
    page1 = await repo.list_students(skip=0, limit=2, school_id="school_page")

    # Then
    assert len(page1) == 2

    # When: 페이지 2 (limit=2)
    page2 = await repo.list_students(skip=2, limit=2, school_id="school_page")

    # Then
    assert len(page2) == 2

    # 서로 다른 학생이어야 함
    page1_ids = {s.id for s in page1}
    page2_ids = {s.id for s in page2}
    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_list_students_by_school(db_session: AsyncSession):
    """학교별 학생 목록 조회 테스트"""
    repo = StudentRepository(db_session)

    # Given: 서로 다른 학교의 학생들 생성
    await repo.create(name="A학교학생1", grade=10, school_id="school_a")
    await repo.create(name="A학교학생2", grade=11, school_id="school_a")
    await repo.create(name="B학교학생1", grade=10, school_id="school_b")

    # When: A학교 학생만 조회
    school_a_students = await repo.list_students(school_id="school_a")

    # Then
    assert len(school_a_students) >= 2
    for student in school_a_students:
        assert student.school_id == "school_a"


@pytest.mark.asyncio
async def test_list_students_by_grade(db_session: AsyncSession):
    """학년별 학생 목록 조회 테스트"""
    repo = StudentRepository(db_session)

    # Given: 서로 다른 학년의 학생들 생성
    await repo.create(name="10학년학생1", grade=10, school_id="school_grade")
    await repo.create(name="10학년학생2", grade=10, school_id="school_grade")
    await repo.create(name="11학년학생1", grade=11, school_id="school_grade")

    # When: 10학년 학생만 조회
    grade_10_students = await repo.list_students(
        school_id="school_grade",
        grade=10
    )

    # Then
    assert len(grade_10_students) >= 2
    for student in grade_10_students:
        assert student.grade == 10


@pytest.mark.asyncio
async def test_update_student(db_session: AsyncSession):
    """학생 정보 수정 테스트"""
    repo = StudentRepository(db_session)

    # Given: 학생 생성
    student = await repo.create(
        name="수정전이름",
        grade=10,
        school_id="school_update"
    )
    original_id = student.id
    original_created_at = student.created_at

    # When: 이름과 학년 수정
    updated = await repo.update(
        student_id=student.id,
        name="수정후이름",
        grade=11
    )

    # Then
    assert updated is not None
    assert updated.id == original_id
    assert updated.name == "수정후이름"
    assert updated.grade == 11
    assert updated.school_id == "school_update"  # 변경 안 됨
    assert updated.created_at == original_created_at  # 변경 안 됨
    assert updated.updated_at > original_created_at  # 업데이트 시간 갱신


@pytest.mark.asyncio
async def test_update_student_not_found(db_session: AsyncSession):
    """존재하지 않는 학생 수정 테스트"""
    repo = StudentRepository(db_session)

    # When: 존재하지 않는 학생 수정 시도
    updated = await repo.update(
        student_id="nonexistent_id",
        name="새이름"
    )

    # Then: None 반환
    assert updated is None


@pytest.mark.asyncio
async def test_delete_student(db_session: AsyncSession):
    """학생 삭제 테스트"""
    repo = StudentRepository(db_session)

    # Given: 학생 생성
    student = await repo.create(
        name="삭제될학생",
        grade=10,
        school_id="school_delete"
    )
    student_id = student.id

    # When: 삭제
    deleted = await repo.delete(student_id)

    # Then: 삭제 성공
    assert deleted is True

    # 조회 시 없어야 함
    found = await repo.get_by_id(student_id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_student_not_found(db_session: AsyncSession):
    """존재하지 않는 학생 삭제 테스트"""
    repo = StudentRepository(db_session)

    # When: 존재하지 않는 학생 삭제 시도
    deleted = await repo.delete("nonexistent_id")

    # Then: False 반환
    assert deleted is False


@pytest.mark.asyncio
async def test_count_students_by_school(db_session: AsyncSession):
    """학교별 학생 수 카운트 테스트"""
    repo = StudentRepository(db_session)

    # Given: 특정 학교에 학생 3명 생성
    school_id = "school_count_test"
    await repo.create(name="카운트1", grade=10, school_id=school_id)
    await repo.create(name="카운트2", grade=11, school_id=school_id)
    await repo.create(name="카운트3", grade=12, school_id=school_id)

    # When: 학교별 카운트
    count = await repo.count_by_school(school_id)

    # Then
    assert count >= 3


@pytest.mark.asyncio
async def test_student_exists(db_session: AsyncSession):
    """학생 존재 여부 확인 테스트"""
    repo = StudentRepository(db_session)

    # Given: 학생 생성
    student = await repo.create(
        name="존재확인학생",
        grade=10,
        school_id="school_exists"
    )

    # When/Then: 존재하는 학생
    exists = await repo.exists(student.id)
    assert exists is True

    # When/Then: 존재하지 않는 학생
    not_exists = await repo.exists("nonexistent_id")
    assert not_exists is False
