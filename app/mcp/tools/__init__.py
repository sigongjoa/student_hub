"""
MCP Tools for Node 0 Student Hub

5 Built-in educational workflow tools.
"""
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from pydantic import BaseModel


class MCPToolBase(ABC):
    """Base class for MCP tools"""

    name: str
    description: str
    input_schema: Dict[str, Any]

    def __init__(self, db_session=None):
        """Initialize tool with optional database session"""
        self.db_session = db_session

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments"""
        raise NotImplementedError


# Import tool registry from tool_registry module
from app.mcp.tool_registry import get_all_tools

# Tool registry (singleton instances)
TOOL_REGISTRY = get_all_tools()


def register_tool(tool: MCPToolBase):
    """Register a tool in the global registry"""
    TOOL_REGISTRY[tool.name] = tool
    return tool
