"""
REST API Gateway for gRPC Backend

FastAPI 서버가 gRPC 백엔드를 호출합니다.
프론트엔드 (/api/v1) <-> REST API (8000) <-> gRPC (50050)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import grpc
import sys
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generated import student_hub_pb2, student_hub_pb2_grpc, workflows_pb2


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 생명주기 관리"""
    # Startup: MCP 클라이언트 초기화
    # TEMPORARILY DISABLED - causing hang during initialization
    # from app.mcp.manager import MCPClientManager
    # await MCPClientManager.get_instance()
    print("Lifespan startup complete (MCP initialization disabled)")
    yield
    # Shutdown: MCP 연결 종료
    # await MCPClientManager.shutdown()
    print("Lifespan shutdown complete")


app = FastAPI(title="Node 0 Student Hub REST API", lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# gRPC 채널 설정
GRPC_HOST = "localhost:50050"


# Pydantic Models
class Student(BaseModel):
    id: Optional[str] = None
    name: str
    grade: int
    school_id: str


class WeeklyDiagnosticRequest(BaseModel):
    student_id: str
    curriculum_path: str
    include_weak_concepts: bool = True


class ErrorReviewRequest(BaseModel):
    student_id: str
    question_id: str
    student_answer: str
    correct_answer: str


class LearningPathRequest(BaseModel):
    student_id: str
    target_concept: str
    days: int = 14


class ExamPrepRequest(BaseModel):
    student_id: str
    exam_date: str
    school_id: str
    curriculum_paths: List[str]


# Health Check
@app.get("/")
async def root():
    return {
        "service": "Node 0 Student Hub REST API",
        "status": "running",
        "grpc_backend": GRPC_HOST,
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    try:
        # gRPC 연결 테스트
        channel = grpc.insecure_channel(GRPC_HOST)
        grpc.channel_ready_future(channel).result(timeout=2)
        channel.close()
        return {"status": "healthy", "grpc": "connected"}
    except Exception as e:
        return {"status": "degraded", "grpc": f"disconnected: {str(e)}"}


# Workflow Endpoints
@app.post("/api/v1/workflows/weekly-diagnostic")
async def start_weekly_diagnostic(request: WeeklyDiagnosticRequest):
    """주간 진단 워크플로우 시작"""
    try:
        async with grpc.aio.insecure_channel(GRPC_HOST) as channel:
            stub = student_hub_pb2_grpc.WorkflowServiceStub(channel)

            grpc_request = workflows_pb2.WeeklyDiagnosticRequest(
                student_id=request.student_id,
                curriculum_path=request.curriculum_path,
                include_weak_concepts=request.include_weak_concepts
            )

            response = await stub.StartWeeklyDiagnostic(grpc_request)

            return {
                "workflow_id": response.workflow_id,
                "session_id": response.session_id,
                "questions": [
                    {
                        "id": q.id,
                        "content": q.content,
                        "difficulty": q.difficulty,
                        "concepts": list(q.concepts)
                    }
                    for q in response.questions
                ],
                "weak_concepts": list(response.weak_concepts),
                "total_estimated_time_minutes": response.total_estimated_time_minutes,
                "started_at": response.started_at
            }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/error-review")
async def start_error_review(request: ErrorReviewRequest):
    """오답 복습 워크플로우 시작"""
    try:
        async with grpc.aio.insecure_channel(GRPC_HOST) as channel:
            stub = student_hub_pb2_grpc.WorkflowServiceStub(channel)

            grpc_request = workflows_pb2.ErrorReviewRequest(
                student_id=request.student_id,
                question_id=request.question_id,
                student_answer=request.student_answer,
                correct_answer=request.correct_answer
            )

            response = await stub.StartErrorReview(grpc_request)

            return {
                "error_note_id": response.error_note_id,
                "next_review_date": response.next_review_date,
                "anki_interval_days": response.anki_interval_days,
                "analysis": {
                    "misconception": response.analysis.misconception,
                    "root_cause": response.analysis.root_cause,
                    "related_concepts": list(response.analysis.related_concepts)
                }
            }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """개인화 학습 경로 생성"""
    try:
        async with grpc.aio.insecure_channel(GRPC_HOST) as channel:
            stub = student_hub_pb2_grpc.WorkflowServiceStub(channel)

            grpc_request = workflows_pb2.LearningPathRequest(
                student_id=request.student_id,
                target_concept=request.target_concept,
                days=request.days
            )

            response = await stub.GenerateLearningPath(grpc_request)

            return {
                "workflow_id": response.workflow_id,
                "learning_path": [
                    {
                        "concept": node.concept,
                        "order": node.order,
                        "estimated_hours": node.estimated_hours,
                        "prerequisites": list(node.prerequisites)
                    }
                    for node in response.learning_path
                ],
                "total_estimated_hours": response.total_estimated_hours,
                "daily_tasks": dict(response.daily_tasks)
            }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/exam-prep")
async def prepare_exam(request: ExamPrepRequest):
    """시험 준비 워크플로우"""
    try:
        async with grpc.aio.insecure_channel(GRPC_HOST) as channel:
            stub = student_hub_pb2_grpc.WorkflowServiceStub(channel)

            grpc_request = workflows_pb2.ExamPrepRequest(
                student_id=request.student_id,
                exam_date=request.exam_date,
                school_id=request.school_id,
                curriculum_paths=request.curriculum_paths
            )

            response = await stub.PrepareExam(grpc_request)

            return {
                "workflow_id": response.workflow_id,
                "two_week_plan": [
                    {
                        "day_number": day.day_number,
                        "date": day.date,
                        "concepts_to_review": list(day.concepts_to_review),
                        "practice_problems": [
                            {
                                "id": p.id,
                                "content": p.content,
                                "difficulty": p.difficulty,
                                "concepts": list(p.concepts)
                            }
                            for p in day.practice_problems
                        ],
                        "anki_reviews": day.anki_reviews
                    }
                    for day in response.two_week_plan.days
                ],
                "focus_concepts": list(response.focus_concepts),
                "mock_exam_pdf_url": response.mock_exam_pdf_url
            }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Student Endpoints (basic CRUD for frontend)
@app.get("/api/v1/students")
async def list_students():
    """학생 목록 조회 (임시 - DB 직접 조회)"""
    try:
        from app.db.session import get_db_session
        from app.models.student import Student as StudentModel
        from sqlalchemy import select

        async with get_db_session() as db:
            stmt = select(StudentModel).limit(100)
            result = await db.execute(stmt)
            students = result.scalars().all()

            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "grade": s.grade,
                    "school_id": s.school_id,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in students
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/students")
async def create_student(student: Student):
    """학생 생성"""
    try:
        from app.db.session import get_db_session
        from app.models.student import Student as StudentModel
        import uuid

        async with get_db_session() as db:
            new_student = StudentModel(
                id=student.id or f"student_{uuid.uuid4().hex[:16]}",
                name=student.name,
                grade=student.grade,
                school_id=student.school_id
            )
            db.add(new_student)
            await db.commit()
            await db.refresh(new_student)

            return {
                "id": new_student.id,
                "name": new_student.name,
                "grade": new_student.grade,
                "school_id": new_student.school_id,
                "created_at": new_student.created_at.isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/students/{student_id}/unified-profile")
async def get_unified_profile(student_id: str):
    """학생 통합 프로필 조회 - Node 2, 4, 7과 통합"""
    try:
        from app.mcp.manager import MCPClientManager
        from app.db.session import get_db_session
        from app.models.student import Student as StudentModel
        from sqlalchemy import select

        # 1. 학생 기본 정보 조회
        async with get_db_session() as db:
            stmt = select(StudentModel).where(StudentModel.id == student_id)
            result = await db.execute(stmt)
            student = result.scalar_one_or_none()

            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            student_data = {
                "id": student.id,
                "name": student.name,
                "grade": student.grade,
                "school_id": student.school_id,
                "created_at": student.created_at.isoformat() if student.created_at else None
            }

        # 2. MCP 클라이언트로 다른 노드에서 데이터 가져오기 (싱글톤 사용)
        mcp_manager = await MCPClientManager.get_instance()

        # Node 2 (Q-DNA): 학생 숙련도
        mastery_data = await mcp_manager.call("q-dna", "get_student_mastery", {
            "student_id": student_id
        })

        # Node 4 (Lab Node): 개념 히트맵
        heatmap_data = await mcp_manager.call("lab-node", "get_concept_heatmap", {
            "student_id": student_id
        })

        # Node 4 (Lab Node): 최근 학습 개념
        recent_concepts_data = await mcp_manager.call("lab-node", "get_recent_concepts", {
            "student_id": student_id
        })

        # Node 4: 약점 개념
        weak_concepts_data = await mcp_manager.call("lab-node", "get_weak_concepts", {
            "student_id": student_id
        })

        # Node 4: 학습 활동 요약
        activity_summary = await mcp_manager.call("lab-node", "get_activity_summary", {
            "student_id": student_id,
            "days": 7
        })

        # Node 7 (Error Note): 오답노트 (빈 응답 처리)
        try:
            error_notes_data = await mcp_manager.call("error-note", "get_due_reviews", {
                "teacher_id": f"teacher_{student.school_id}",
                "date": "2026-01-10"
            })
        except:
            error_notes_data = {"reviews": []}

        # 3. 통합 프로필 생성 (프론트엔드 UnifiedProfile 타입에 맞게)
        # Node 4 heatmap 데이터 사용
        concept_scores = heatmap_data.get("heatmap", {}) if isinstance(heatmap_data, dict) else {}

        # Node 4 activity summary 사용
        total_attempts = activity_summary.get("total_attempts", 0)
        average_mastery = activity_summary.get("average_accuracy", 0.0)

        # 최근 개념으로 활동 생성
        recent_concepts_list = recent_concepts_data.get("concepts", [])
        recent_activities = []
        for concept in recent_concepts_list[:3]:
            score = concept_scores.get(concept, 0.5)
            recent_activities.append({
                "date": heatmap_data.get("timestamp", "2026-01-11T13:40:00"),
                "type": f"Practice: {concept}",
                "score": int(score * 100)
            })

        unified_profile = {
            "student_id": student_id,
            "basic_info": {
                "name": student.name,
                "grade": student.grade,
                "school_code": student.school_id
            },
            "mastery_summary": {
                "average": average_mastery,
                "total_attempts": total_attempts,
                "recent_trend": "Improving" if average_mastery > 0.6 else "Stable"
            },
            "recent_activities": recent_activities,
            "latest_reports": [],
            "heatmap_data": concept_scores,
            "generated_at": heatmap_data.get("timestamp", "2026-01-11T13:40:00")
        }

        return unified_profile

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching unified profile: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
