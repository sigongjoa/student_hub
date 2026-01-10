import asyncio
import logging
from concurrent import futures
import grpc
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from generated import student_hub_pb2_grpc

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


from app.grpc_services.workflow_service import WorkflowServiceServicer


# Placeholder for StudentHubService (will be implemented later)
class StudentHubServiceServicer(student_hub_pb2_grpc.StudentHubServiceServicer):
    """학생 관리 서비스 (향후 구현)"""
    pass


async def serve():
    """gRPC 서버 시작"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=settings.GRPC_MAX_WORKERS)
    )

    # 서비스 등록
    student_hub_pb2_grpc.add_StudentHubServiceServicer_to_server(
        StudentHubServiceServicer(), server
    )
    student_hub_pb2_grpc.add_WorkflowServiceServicer_to_server(
        WorkflowServiceServicer(), server
    )

    # 포트 바인딩
    listen_addr = f'[::]:{settings.GRPC_PORT}'
    server.add_insecure_port(listen_addr)

    logger.info(f"🚀 Starting gRPC server on port {settings.GRPC_PORT}...")
    logger.info(f"📡 Listening on {listen_addr}")

    await server.start()

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("⏹️  Shutting down gRPC server...")
        await server.stop(grace=5)


if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("✅ Server stopped")
