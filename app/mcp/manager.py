"""
MCP Client Manager

Manages all MCP clients (gRPC-based real servers).
"""
from typing import Dict, Any, Optional
from app.mcp.grpc_client import GRPCMCPClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP Client Manager - gRPC based"""

    _instance: Optional['MCPClientManager'] = None
    _initialized: bool = False

    def __init__(self):
        # Create gRPC clients for real servers
        self.clients = {
            "q-dna": GRPCMCPClient("q-dna", "localhost", 50052),
            "lab-node": GRPCMCPClient("lab-node", "localhost", 50053),
            "error-note": GRPCMCPClient("error-note", "localhost", 50054)
        }
        logger.info(f"Initialized MCPClientManager with {len(self.clients)} gRPC clients")

    @classmethod
    async def get_instance(cls) -> 'MCPClientManager':
        """Get singleton instance"""
        if cls._instance is None:
            logger.info("Creating new MCPClientManager singleton instance")
            cls._instance = cls()
            await cls._instance.initialize()
            cls._initialized = True
        return cls._instance

    async def initialize(self):
        """Connect all clients"""
        for name, client in self.clients.items():
            await client.connect()

    async def call(self, node: str, tool: str, params: Dict[str, Any]) -> Any:
        """Route MCP call to appropriate client"""
        client = self.clients.get(node)
        if not client:
            raise ValueError(f"Unknown node: {node}")

        return await client.call_tool(tool, params)

    async def close_all(self):
        """Close all connections"""
        for client in self.clients.values():
            await client.close()

    @classmethod
    async def shutdown(cls):
        """Shutdown singleton"""
        if cls._instance:
            logger.info("Shutting down MCPClientManager singleton")
            await cls._instance.close_all()
            cls._instance = None
            cls._initialized = False
