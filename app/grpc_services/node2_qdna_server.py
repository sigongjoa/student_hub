"""
Node 2 (Q-DNA) gRPC MCP Server

Provides BKT-based mastery calculation and IRT-based question recommendation.
Port: 50052
"""
import grpc
import asyncio
import logging
from concurrent import futures
from datetime import datetime
from typing import Dict, Any, List
import random

from generated import node2_qdna_pb2, node2_qdna_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QDNAServicer(node2_qdna_pb2_grpc.QDNAServiceServicer):
    """Q-DNA gRPC Service Implementation"""
    
    def __init__(self):
        # In-memory storage for student mastery data (simulating database)
        self.student_mastery_data: Dict[str, Dict[str, float]] = {}
    
    async def GetStudentMastery(
        self,
        request: node2_qdna_pb2.GetStudentMasteryRequest,
        context: grpc.aio.ServicerContext
    ) -> node2_qdna_pb2.GetStudentMasteryResponse:
        """Get student mastery scores for concepts"""
        logger.info(f"GetStudentMastery called for student: {request.student_id}")
        
        student_id = request.student_id
        concepts = list(request.concepts) if request.concepts else list(request.skill_ids)
        
        # Get or initialize mastery data
        if student_id not in self.student_mastery_data:
            self.student_mastery_data[student_id] = {
                "도함수": random.uniform(0.3, 0.7),
                "적분": random.uniform(0.3, 0.7),
                "극한": random.uniform(0.3, 0.7),
                "미분": random.uniform(0.3, 0.7),
                "삼각함수": random.uniform(0.5, 0.9),
                "이차함수": random.uniform(0.4, 0.8),
                "방정식": random.uniform(0.5, 0.85)
            }
        
        mastery = self.student_mastery_data[student_id]
        
        # Filter by requested concepts if provided
        if concepts:
            result_mastery = {c: mastery.get(c, 0.5) for c in concepts}
        else:
            result_mastery = mastery
        
        return node2_qdna_pb2.GetStudentMasteryResponse(mastery=result_mastery)
    
    async def RecommendQuestions(
        self,
        request: node2_qdna_pb2.RecommendQuestionsRequest,
        context: grpc.aio.ServicerContext
    ) -> node2_qdna_pb2.RecommendQuestionsResponse:
        """Recommend questions based on student mastery"""
        logger.info(f"RecommendQuestions called for student: {request.student_id}")
        
        # Determine target concepts
        if request.weak_concepts:
            target_concepts = list(request.weak_concepts)
        elif request.concept:
            target_concepts = [request.concept]
        else:
            target_concepts = ["도함수", "적분"]
        
        # Generate questions
        questions = []
        difficulty = request.difficulty or "medium"
        count = request.count or 10
        
        for i in range(count):
            selected_concept = random.choice(target_concepts)
            questions.append(node2_qdna_pb2.Question(
                id=f"q_{selected_concept}_{difficulty}_{i+1}",
                content=f"{selected_concept} 관련 {difficulty} 난이도 문제 {i+1}",
                difficulty=difficulty,
                concepts=[selected_concept],
                estimated_time_minutes=3 if difficulty == "easy" else 5 if difficulty == "medium" else 8
            ))
        
        return node2_qdna_pb2.RecommendQuestionsResponse(
            questions=questions,
            student_id=request.student_id,
            count=len(questions)
        )
    
    async def GetQuestionDNA(
        self,
        request: node2_qdna_pb2.GetQuestionDNARequest,
        context: grpc.aio.ServicerContext
    ) -> node2_qdna_pb2.GetQuestionDNAResponse:
        """Get question DNA (difficulty, concepts, Bloom level)"""
        logger.info(f"GetQuestionDNA called for question: {request.question_id}")
        
        return node2_qdna_pb2.GetQuestionDNAResponse(
            question_id=request.question_id,
            difficulty="medium",
            concepts=["도함수", "극한"],
            bloom_level="apply"
        )
    
    async def EstimateLearningTime(
        self,
        request: node2_qdna_pb2.EstimateLearningTimeRequest,
        context: grpc.aio.ServicerContext
    ) -> node2_qdna_pb2.EstimateLearningTimeResponse:
        """Estimate learning time for a concept"""
        logger.info(f"EstimateLearningTime called for concept: {request.concept}")
        
        concept = request.concept
        current_mastery = request.current_mastery
        
        # Base hours per concept
        base_hours = {"극한": 4, "도함수": 6, "적분": 8, "미분": 5, "삼각함수": 3}.get(concept, 4)
        
        # Adjust based on current mastery
        adjustment = (1.0 - current_mastery) * 2
        estimated_hours = int(base_hours + adjustment)
        
        return node2_qdna_pb2.EstimateLearningTimeResponse(
            concept=concept,
            estimated_hours=estimated_hours,
            current_mastery=current_mastery
        )


async def serve():
    """Start Node 2 gRPC Server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    node2_qdna_pb2_grpc.add_QDNAServiceServicer_to_server(QDNAServicer(), server)
    
    server.add_insecure_port('[::]:50052')
    logger.info("🚀 Node 2 (Q-DNA) gRPC Server starting on port 50052...")
    await server.start()
    logger.info("✅ Node 2 (Q-DNA) gRPC Server started successfully!")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
