"""
Workflow Service - gRPC 구현

5가지 워크플로우 RPC 메서드를 구현합니다.
"""
import grpc
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from generated import student_hub_pb2, student_hub_pb2_grpc, workflows_pb2
from app.services.weekly_diagnostic_service import (
    WeeklyDiagnosticService,
    WeeklyDiagnosticRequest
)
from app.services.error_review_service import (
    ErrorReviewService,
    ErrorReviewRequest
)
from app.services.learning_path_service import (
    LearningPathService,
    LearningPathRequest
)
from app.services.exam_prep_service import (
    ExamPrepService,
    ExamPrepRequest
)
from app.mcp.manager import MCPClientManager
from app.db.session import get_db_session

logger = logging.getLogger(__name__)


class WorkflowServiceServicer(student_hub_pb2_grpc.WorkflowServiceServicer):
    """워크플로우 서비스 gRPC 구현"""

    def __init__(self):
        self.mcp = MCPClientManager()
        logger.info("WorkflowServiceServicer initialized")

    async def StartWeeklyDiagnostic(
        self,
        request: workflows_pb2.WeeklyDiagnosticRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.WeeklyDiagnosticResponse:
        """주간 진단 워크플로우 시작"""
        try:
            logger.info(f"StartWeeklyDiagnostic called for student {request.student_id}")

            async with get_db_session() as db:
                service = WeeklyDiagnosticService(self.mcp, db)

                service_request = WeeklyDiagnosticRequest(
                    student_id=request.student_id,
                    curriculum_path=request.curriculum_path,
                    include_weak_concepts=request.include_weak_concepts
                )

                result = await service.start_diagnostic(service_request)

                # Protobuf 메시지로 변환
                return workflows_pb2.WeeklyDiagnosticResponse(
                    workflow_id=result.workflow_id,
                    session_id=str(result.session_id),
                    questions=[
                        workflows_pb2.Question(
                            id=q.id,
                            content=q.content,
                            difficulty=q.difficulty,
                            concepts=q.concepts
                        )
                        for q in result.questions
                    ],
                    weak_concepts=result.weak_concepts,
                    total_estimated_time_minutes=result.total_estimated_time_minutes,
                    started_at=result.started_at.isoformat()
                )

        except Exception as e:
            logger.error(f"StartWeeklyDiagnostic failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def StartErrorReview(
        self,
        request: workflows_pb2.ErrorReviewRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.ErrorReviewResponse:
        """오답 복습 워크플로우 시작"""
        try:
            logger.info(f"StartErrorReview called for student {request.student_id}, question {request.question_id}")

            async with get_db_session() as db:
                service = ErrorReviewService(self.mcp, db)

                service_request = ErrorReviewRequest(
                    student_id=request.student_id,
                    question_id=request.question_id,
                    student_answer=request.student_answer,
                    correct_answer=request.correct_answer
                )

                result = await service.start_error_review(service_request)

                # Protobuf 메시지로 변환
                return workflows_pb2.ErrorReviewResponse(
                    error_note_id=result.error_note_id,
                    next_review_date=result.next_review_date.isoformat(),
                    anki_interval_days=result.anki_interval_days,
                    analysis=workflows_pb2.ErrorAnalysis(
                        misconception=result.analysis.misconception,
                        root_cause=result.analysis.root_cause,
                        related_concepts=result.analysis.related_concepts
                    )
                )

        except Exception as e:
            logger.error(f"StartErrorReview failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GenerateLearningPath(
        self,
        request: workflows_pb2.LearningPathRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.LearningPathResponse:
        """개인화 학습 경로 생성"""
        try:
            logger.info(f"GenerateLearningPath called for student {request.student_id}, target: {request.target_concept}")

            async with get_db_session() as db:
                service = LearningPathService(self.mcp, db)

                service_request = LearningPathRequest(
                    student_id=request.student_id,
                    target_concept=request.target_concept,
                    days=request.days
                )

                result = await service.generate_learning_path(service_request)

                # Protobuf 메시지로 변환
                return workflows_pb2.LearningPathResponse(
                    workflow_id=result.workflow_id,
                    learning_path=[
                        workflows_pb2.PathNode(
                            concept=node.concept,
                            order=node.order,
                            estimated_hours=node.estimated_hours,
                            prerequisites=node.prerequisites
                        )
                        for node in result.learning_path
                    ],
                    total_estimated_hours=result.total_estimated_hours,
                    daily_tasks=result.daily_tasks
                )

        except Exception as e:
            logger.error(f"GenerateLearningPath failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetClassAnalytics(
        self,
        request: workflows_pb2.ClassAnalyticsRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.ClassAnalyticsResponse:
        """클래스 분석 (향후 구현)"""
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not implemented yet")

    async def PrepareExam(
        self,
        request: workflows_pb2.ExamPrepRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.ExamPrepResponse:
        """시험 준비"""
        try:
            logger.info(f"PrepareExam called for student {request.student_id}, exam: {request.exam_date}")

            async with get_db_session() as db:
                service = ExamPrepService(self.mcp, db)

                service_request = ExamPrepRequest(
                    student_id=request.student_id,
                    exam_date=request.exam_date,
                    school_id=request.school_id,
                    curriculum_paths=list(request.curriculum_paths)
                )

                result = await service.prepare_exam(service_request)

                # Protobuf 메시지로 변환
                return workflows_pb2.ExamPrepResponse(
                    workflow_id=result.workflow_id,
                    two_week_plan=workflows_pb2.StudyPlan(
                        days=[
                            workflows_pb2.DailyTask(
                                day_number=task.day_number,
                                date=task.date,
                                concepts_to_review=task.concepts_to_review,
                                practice_problems=[
                                    workflows_pb2.Question(
                                        id=p.get("id", ""),
                                        content=p.get("content", ""),
                                        difficulty=p.get("difficulty", "medium"),
                                        concepts=p.get("concepts", [])
                                    )
                                    for p in task.practice_problems
                                ],
                                anki_reviews=task.anki_reviews
                            )
                            for task in result.two_week_plan
                        ]
                    ),
                    practice_problems=[
                        workflows_pb2.Question(
                            id=p.get("id", ""),
                            content=p.get("content", ""),
                            difficulty=p.get("difficulty", "medium"),
                            concepts=p.get("concepts", [])
                        )
                        for p in result.practice_problems
                    ],
                    focus_concepts=result.focus_concepts,
                    mock_exam_pdf_url=result.mock_exam_pdf_url
                )

        except Exception as e:
            logger.error(f"PrepareExam failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetWorkflowStatus(
        self,
        request: workflows_pb2.GetWorkflowStatusRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.WorkflowStatusResponse:
        """워크플로우 상태 조회 (향후 구현)"""
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not implemented yet")
