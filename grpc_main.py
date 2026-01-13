"""
Node 0 MCP gRPC Server

LLM이 자연어로 워크플로우를 실행할 수 있도록 MCP tools를 제공하는 gRPC 서버
"""
import asyncio
import logging
from concurrent import futures
import grpc

from generated import node0_mcp_pb2_grpc
from app.grpc_services import Node0MCPServicer
from app.config import settings

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def serve():
    """gRPC 서버 시작"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
        ]
    )

    # Service 등록
    node0_mcp_pb2_grpc.add_Node0MCPServiceServicer_to_server(
        Node0MCPServicer(), server
    )

    # Port 바인딩
    port = getattr(settings, 'GRPC_MCP_PORT', 50051)
    server.add_insecure_port(f'[::]:{port}')

    logger.info(f"🚀 Starting Node 0 MCP gRPC Server on port {port}...")
    logger.info(f"   Built-in tools: 5")
    logger.info(f"   Custom tools: DB-based")
    logger.info(f"   Workflow templates: DB-based")

    await server.start()
    logger.info("✅ Server started successfully")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("⏹ Shutting down server...")
        await server.stop(grace=5)
        logger.info("✅ Server stopped")


if __name__ == '__main__':
    asyncio.run(serve())
