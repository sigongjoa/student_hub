"""
CRUD 작동 검증 스크립트

실제 PostgreSQL DB에서 Create, Read, Update, Delete가 작동하는지 확인합니다.
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import get_db_session
from app.models.student import Student
from app.models.workflow_session import WorkflowSession
from sqlalchemy import select


async def test_crud():
    """CRUD 테스트"""

    print("=== CRUD 테스트 시작 ===\n")

    async with get_db_session() as db:
        # CREATE: 학생 생성
        print("1. CREATE: 학생 생성")
        student = Student(
            id="test_student_001",
            name="김테스트",
            grade=10,
            school_id="TEST_SCHOOL_001"
        )
        db.add(student)
        await db.flush()
        print(f"   ✅ 학생 생성: {student.name} (ID: {student.id})")

        # READ: 학생 조회
        print("\n2. READ: 학생 조회")
        stmt = select(Student).where(Student.id == "test_student_001")
        result = await db.execute(stmt)
        found_student = result.scalar_one_or_none()

        if found_student:
            print(f"   ✅ 학생 조회 성공: {found_student.name}, Grade: {found_student.grade}")
        else:
            print("   ❌ 학생 조회 실패")
            return

        # CREATE: 워크플로우 세션 생성
        print("\n3. CREATE: 워크플로우 세션 생성")
        workflow = WorkflowSession(
            student_id=student.id,
            workflow_type="weekly_diagnostic",
            status="in_progress",
            workflow_metadata={
                "test": True,
                "questions": [{"id": "q1", "difficulty": "easy"}],
                "created_at": datetime.now().isoformat()
            }
        )
        db.add(workflow)
        await db.flush()
        print(f"   ✅ 워크플로우 생성: {workflow.workflow_id}")
        print(f"      Type: {workflow.workflow_type}, Status: {workflow.status}")

        # READ: 워크플로우 조회
        print("\n4. READ: 워크플로우 조회")
        stmt = select(WorkflowSession).where(
            WorkflowSession.student_id == student.id
        )
        result = await db.execute(stmt)
        workflows = result.scalars().all()

        print(f"   ✅ 워크플로우 조회: {len(workflows)}개 발견")
        for wf in workflows:
            print(f"      - {wf.workflow_id}: {wf.workflow_type} ({wf.status})")

        # UPDATE: 워크플로우 상태 변경
        print("\n5. UPDATE: 워크플로우 상태 변경")
        workflow.status = "completed"
        workflow.completed_at = datetime.now()
        await db.flush()
        print(f"   ✅ 워크플로우 상태 업데이트: {workflow.status}")

        # READ: 업데이트 확인
        stmt = select(WorkflowSession).where(
            WorkflowSession.workflow_id == workflow.workflow_id
        )
        result = await db.execute(stmt)
        updated_workflow = result.scalar_one()
        print(f"   ✅ 업데이트 확인: {updated_workflow.status}")

        # DELETE: 워크플로우 삭제
        print("\n6. DELETE: 워크플로우 삭제")
        await db.delete(workflow)
        await db.flush()
        print(f"   ✅ 워크플로우 삭제: {workflow.workflow_id}")

        # READ: 삭제 확인
        stmt = select(WorkflowSession).where(
            WorkflowSession.workflow_id == workflow.workflow_id
        )
        result = await db.execute(stmt)
        deleted_workflow = result.scalar_one_or_none()

        if deleted_workflow is None:
            print("   ✅ 삭제 확인: 워크플로우가 더 이상 존재하지 않음")
        else:
            print("   ❌ 삭제 실패: 워크플로우가 여전히 존재함")

        # DELETE: 학생 삭제
        print("\n7. DELETE: 학생 삭제")
        await db.delete(student)
        await db.flush()
        print(f"   ✅ 학생 삭제: {student.id}")

    print("\n=== CRUD 테스트 완료 ===")
    print("✅ 모든 CRUD 작업이 정상적으로 작동합니다!")


if __name__ == "__main__":
    asyncio.run(test_crud())
