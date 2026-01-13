"""
Node 4 (Lab Node) gRPC MCP Server

Provides student activity data and analytics.
Port: 50053
"""
import grpc
import asyncio
import logging
from concurrent import futures
from datetime import datetime
from typing import Dict, Any, List
import random

from generated import node4_labnode_pb2, node4_labnode_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabNodeServicer(node4_labnode_pb2_grpc.LabNodeServiceServicer):
    """Lab Node gRPC Service Implementation"""
    
    def __init__(self):
        # In-memory storage for activity data
        self.student_activity_data: Dict[str, List[Dict[str, Any]]] = {}
    
    async def GetRecentConcepts(
        self,
        request: node4_labnode_pb2.GetRecentConceptsRequest,
        context: grpc.aio.ServicerContext
    ) -> node4_labnode_pb2.GetRecentConceptsResponse:
        """Get recent learning concepts"""
        logger.info(f"GetRecentConcepts called for student: {request.student_id}")
        
        concepts = ["도함수", "적분", "극한", "미분"] if random.random() > 0.3 else ["삼각함수", "이차함수"]
        
        return node4_labnode_pb2.GetRecentConceptsResponse(
            concepts=concepts,
            student_id=request.student_id,
            period_days=request.days or 7
        )
    
    async def GetConceptHeatmap(
        self,
        request: node4_labnode_pb2.GetConceptHeatmapRequest,
        context: grpc.aio.ServicerContext
    ) -> node4_labnode_pb2.GetConceptHeatmapResponse:
        """Get concept accuracy heatmap"""
        logger.info(f"GetConceptHeatmap called for student: {request.student_id}")
        
        heatmap = {
            "극한": random.uniform(0.4, 0.6),
            "도함수": random.uniform(0.5, 0.7),
            "적분": random.uniform(0.3, 0.5),
            "미분": random.uniform(0.6, 0.8),
            "삼각함수": random.uniform(0.7, 0.9)
        }
        
        return node4_labnode_pb2.GetConceptHeatmapResponse(
            student_id=request.student_id,
            heatmap=heatmap,
            timestamp=datetime.now().isoformat()
        )
    
    async def GetWeakConcepts(
        self,
        request: node4_labnode_pb2.GetWeakConceptsRequest,
        context: grpc.aio.ServicerContext
    ) -> node4_labnode_pb2.GetWeakConceptsResponse:
        """Get weak concepts"""
        logger.info(f"GetWeakConcepts called for student: {request.student_id}")
        
        weak_concepts = [
            node4_labnode_pb2.WeakConcept(concept="도함수", accuracy=0.45, attempts=20),
            node4_labnode_pb2.WeakConcept(concept="극한", accuracy=0.50, attempts=15),
            node4_labnode_pb2.WeakConcept(concept="적분", accuracy=0.35, attempts=10)
        ]
        
        limit = request.limit or 10
        return node4_labnode_pb2.GetWeakConceptsResponse(
            weak_concepts=weak_concepts[:limit]
        )
    
    async def GetActivitySummary(
        self,
        request: node4_labnode_pb2.GetActivitySummaryRequest,
        context: grpc.aio.ServicerContext
    ) -> node4_labnode_pb2.GetActivitySummaryResponse:
        """Get student activity summary"""
        logger.info(f"GetActivitySummary called for student: {request.student_id}")
        
        return node4_labnode_pb2.GetActivitySummaryResponse(
            student_id=request.student_id,
            period_days=request.days or 7,
            total_attempts=100,
            average_accuracy=0.56,
            concepts_practiced=5,
            last_activity=datetime.now().isoformat(),
            timestamp=datetime.now().isoformat()
        )
    
    async def GetClassAnalytics(
        self,
        request: node4_labnode_pb2.GetClassAnalyticsRequest,
        context: grpc.aio.ServicerContext
    ) -> node4_labnode_pb2.GetClassAnalyticsResponse:
        """Get class analytics"""
        logger.info(f"GetClassAnalytics called for class: {request.class_id}")
        
        total = random.randint(20, 40)
        active = random.randint(15, min(35, total))
        
        return node4_labnode_pb2.GetClassAnalyticsResponse(
            total_students=total,
            active_students=active,
            average_accuracy=round(random.uniform(0.55, 0.75), 2),
            at_risk_students=random.randint(2, min(8, total)),
            common_weak_concepts=[
                node4_labnode_pb2.CommonWeakConcept(concept="적분", struggling_count=random.randint(5, 15)),
                node4_labnode_pb2.CommonWeakConcept(concept="극한", struggling_count=random.randint(3, 12))
            ]
        )


async def serve():
    """Start Node 4 gRPC Server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    node4_labnode_pb2_grpc.add_LabNodeServiceServicer_to_server(LabNodeServicer(), server)
    
    server.add_insecure_port('[::]:50053')
    logger.info("🚀 Node 4 (Lab Node) gRPC Server starting on port 50053...")
    await server.start()
    logger.info("✅ Node 4 (Lab Node) gRPC Server started successfully!")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
