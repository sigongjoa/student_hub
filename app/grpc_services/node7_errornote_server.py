"""
Node 7 (Error Note) gRPC MCP Server

Provides error analysis and Anki SM-2 scheduling.
Port: 50054
"""
import grpc
import asyncio
import logging
from concurrent import futures
from datetime import datetime, timedelta
from typing import Dict, Any
import random
import uuid

from generated import node7_errornote_pb2, node7_errornote_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorNoteServicer(node7_errornote_pb2_grpc.ErrorNoteServiceServicer):
    """Error Note gRPC Service Implementation"""
    
    def __init__(self):
        # In-memory storage for error notes
        self.error_notes: Dict[str, Dict[str, Any]] = {}
    
    async def CreateErrorNote(
        self,
        request: node7_errornote_pb2.CreateErrorNoteRequest,
        context: grpc.aio.ServicerContext
    ) -> node7_errornote_pb2.CreateErrorNoteResponse:
        """Create error note"""
        logger.info(f"CreateErrorNote called for student: {request.student_id}")
        
        error_note_id = f"en_{uuid.uuid4().hex[:16]}"
        created_at = datetime.now().isoformat()
        
        # Analyze error
        analysis = node7_errornote_pb2.ErrorAnalysis(
            misconception="이차함수의 최댓값 개념 혼동",
            root_cause="위로 볼록/아래로 볼록 판단 오류",
            related_concepts=["이차함수", "도함수", "극값"]
        )
        
        # Initialize Anki data (SM-2 algorithm)
        anki_data = node7_errornote_pb2.AnkiData(
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review=(datetime.now() + timedelta(days=1)).isoformat()
        )
        
        # Store error note
        self.error_notes[error_note_id] = {
            "id": error_note_id,
            "student_id": request.student_id,
            "question_id": request.question_id,
            "student_answer": request.student_answer,
            "correct_answer": request.correct_answer,
            "created_at": created_at,
            "analysis": analysis,
            "anki_data": anki_data
        }
        
        return node7_errornote_pb2.CreateErrorNoteResponse(
            id=error_note_id,
            created_at=created_at,
            analysis=analysis,
            anki_data=anki_data
        )
    
    async def GetErrorNote(
        self,
        request: node7_errornote_pb2.GetErrorNoteRequest,
        context: grpc.aio.ServicerContext
    ) -> node7_errornote_pb2.GetErrorNoteResponse:
        """Get error note by ID"""
        logger.info(f"GetErrorNote called for: {request.error_note_id}")
        
        note = self.error_notes.get(request.error_note_id)
        if not note:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Error note not found")
        
        return node7_errornote_pb2.GetErrorNoteResponse(
            id=note["id"],
            student_id=note["student_id"],
            question_id=note["question_id"],
            student_answer=note["student_answer"],
            correct_answer=note["correct_answer"],
            created_at=note["created_at"],
            analysis=note["analysis"],
            anki_data=note["anki_data"]
        )
    
    async def ListErrorNotesByStudent(
        self,
        request: node7_errornote_pb2.ListErrorNotesByStudentRequest,
        context: grpc.aio.ServicerContext
    ) -> node7_errornote_pb2.ListErrorNotesByStudentResponse:
        """List all error notes for a student"""
        logger.info(f"ListErrorNotesByStudent called for: {request.student_id}")
        
        student_notes = [
            node7_errornote_pb2.GetErrorNoteResponse(
                id=note["id"],
                student_id=note["student_id"],
                question_id=note["question_id"],
                student_answer=note["student_answer"],
                correct_answer=note["correct_answer"],
                created_at=note["created_at"],
                analysis=note["analysis"],
                anki_data=note["anki_data"]
            )
            for note in self.error_notes.values()
            if note["student_id"] == request.student_id
        ]
        
        return node7_errornote_pb2.ListErrorNotesByStudentResponse(
            error_notes=student_notes
        )
    
    async def CalculateAnkiSchedule(
        self,
        request: node7_errornote_pb2.CalculateAnkiScheduleRequest,
        context: grpc.aio.ServicerContext
    ) -> node7_errornote_pb2.CalculateAnkiScheduleResponse:
        """Calculate Anki SM-2 schedule"""
        logger.info(f"CalculateAnkiSchedule called for: {request.error_note_id}")
        
        note = self.error_notes.get(request.error_note_id)
        if not note:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Error note not found")
        
        quality = request.quality
        current_anki = note["anki_data"]
        
        # SM-2 Algorithm
        if quality >= 3:
            if current_anki.repetitions == 0:
                interval = 1
            elif current_anki.repetitions == 1:
                interval = 6
            else:
                interval = int(current_anki.interval_days * current_anki.ease_factor)
            
            ease_factor = current_anki.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            ease_factor = max(1.3, ease_factor)
            repetitions = current_anki.repetitions + 1
        else:
            interval = 1
            ease_factor = current_anki.ease_factor
            repetitions = 0
        
        next_review = (datetime.now() + timedelta(days=interval)).isoformat()
        
        # Update stored data
        new_anki = node7_errornote_pb2.AnkiData(
            ease_factor=ease_factor,
            interval_days=interval,
            repetitions=repetitions,
            next_review=next_review
        )
        note["anki_data"] = new_anki
        
        return node7_errornote_pb2.CalculateAnkiScheduleResponse(
            ease_factor=ease_factor,
            interval_days=interval,
            next_review_date=next_review
        )
    
    async def GetDueReviews(
        self,
        request: node7_errornote_pb2.GetDueReviewsRequest,
        context: grpc.aio.ServicerContext
    ) -> node7_errornote_pb2.GetDueReviewsResponse:
        """Get due reviews for a student"""
        logger.info(f"GetDueReviews called for student: {request.student_id}")
        
        target_date = datetime.fromisoformat(request.date) if request.date else datetime.now()
        
        due_notes = [
            node7_errornote_pb2.GetErrorNoteResponse(
                id=note["id"],
                student_id=note["student_id"],
                question_id=note["question_id"],
                student_answer=note["student_answer"],
                correct_answer=note["correct_answer"],
                created_at=note["created_at"],
                analysis=note["analysis"],
                anki_data=note["anki_data"]
            )
            for note in self.error_notes.values()
            if note["student_id"] == request.student_id
            and datetime.fromisoformat(note["anki_data"].next_review) <= target_date
        ]
        
        return node7_errornote_pb2.GetDueReviewsResponse(due_notes=due_notes)
    
    async def DeleteErrorNote(
        self,
        request: node7_errornote_pb2.DeleteErrorNoteRequest,
        context: grpc.aio.ServicerContext
    ) -> node7_errornote_pb2.DeleteErrorNoteResponse:
        """Delete error note"""
        logger.info(f"DeleteErrorNote called for: {request.error_note_id}")
        
        if request.error_note_id in self.error_notes:
            del self.error_notes[request.error_note_id]
            return node7_errornote_pb2.DeleteErrorNoteResponse(
                success=True,
                message="Error note deleted successfully"
            )
        else:
            return node7_errornote_pb2.DeleteErrorNoteResponse(
                success=False,
                message="Error note not found"
            )


async def serve():
    """Start Node 7 gRPC Server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    node7_errornote_pb2_grpc.add_ErrorNoteServiceServicer_to_server(ErrorNoteServicer(), server)
    
    server.add_insecure_port('[::]:50054')
    logger.info("🚀 Node 7 (Error Note) gRPC Server starting on port 50054...")
    await server.start()
    logger.info("✅ Node 7 (Error Note) gRPC Server started successfully!")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
