"""
MCP Tool Registry

Registers all 5 built-in tools.
"""
from typing import Dict, Type
from app.mcp.tools import MCPToolBase
from app.mcp.tools.weekly_diagnostic import AnalyzeStudentWeaknessesTool
from app.mcp.tools.error_review import CreateErrorReviewTool
from app.mcp.tools.learning_path import GenerateLearningPathTool
from app.mcp.tools.exam_prep import PrepareExamTool
from app.mcp.tools.student_profile import GetStudentProfileTool


# Tool classes
TOOL_CLASSES: Dict[str, Type[MCPToolBase]] = {
    "analyze_student_weaknesses": AnalyzeStudentWeaknessesTool,
    "create_error_review": CreateErrorReviewTool,
    "generate_learning_path": GenerateLearningPathTool,
    "prepare_exam": PrepareExamTool,
    "get_student_profile": GetStudentProfileTool
}


def get_all_tools() -> Dict[str, MCPToolBase]:
    """Get instances of all tools (without DB session)"""
    return {
        name: tool_class()
        for name, tool_class in TOOL_CLASSES.items()
    }


def get_tool_metadata():
    """Get metadata for all tools (for ListTools RPC)"""
    tools = get_all_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema
        }
        for tool in tools.values()
    ]
