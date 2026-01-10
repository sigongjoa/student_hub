"""
MCP Client Manager

모든 MCP 클라이언트를 관리하고 요청을 라우팅합니다.
"""
from typing import Dict, Any
from app.mcp.client import MCPClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP 클라이언트 관리자"""

    def __init__(self):
        self.clients = {
            "q-dna": MCPClient("q-dna", settings.NODE2_MCP_PATH),
            "lab-node": MCPClient("lab-node", settings.NODE4_MCP_PATH),
            "error-note": MCPClient("error-note", settings.NODE7_MCP_PATH)
        }
        logger.info(f"Initialized MCPClientManager with {len(self.clients)} clients")

    async def initialize(self):
        """모든 클라이언트 연결"""
        for name, client in self.clients.items():
            await client.connect()

    async def call(self, node: str, tool: str, params: Dict[str, Any]) -> Any:
        """MCP 호출 라우팅"""
        client = self.clients.get(node)
        if not client:
            raise ValueError(f"Unknown node: {node}")

        return await client.call_tool(tool, params)

    async def close_all(self):
        """모든 연결 종료"""
        for client in self.clients.values():
            await client.close()
