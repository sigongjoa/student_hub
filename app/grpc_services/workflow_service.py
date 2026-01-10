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
        """개인화 학습 경로 생성 (향후 구현)"""
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not implemented yet")

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
        """시험 준비 (향후 구현)"""
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not implemented yet")

    async def GetWorkflowStatus(
        self,
        request: workflows_pb2.GetWorkflowStatusRequest,
        context: grpc.aio.ServicerContext
    ) -> workflows_pb2.WorkflowStatusResponse:
        """워크플로우 상태 조회 (향후 구현)"""
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not implemented yet")
