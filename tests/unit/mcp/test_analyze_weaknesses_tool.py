"""
TDD Tests for AnalyzeStudentWeaknessesTool

RED phase: Write failing tests first
"""
import pytest
from app.mcp.tools.weekly_diagnostic import AnalyzeStudentWeaknessesTool


@pytest.mark.asyncio
async def test_tool_has_correct_metadata():
    """Tool should have name, description, and schema"""
    tool = AnalyzeStudentWeaknessesTool()
    
    assert tool.name == "analyze_student_weaknesses"
    assert isinstance(tool.description, str)
    assert len(tool.description) > 0
    assert isinstance(tool.input_schema, dict)
    assert "type" in tool.input_schema
    assert tool.input_schema["type"] == "object"


@pytest.mark.asyncio
async def test_tool_schema_has_required_fields():
    """Schema should define student_id and curriculum_path as required"""
    tool = AnalyzeStudentWeaknessesTool()
    
    schema = tool.input_schema
    assert "properties" in schema
    assert "student_id" in schema["properties"]
    assert "curriculum_path" in schema["properties"]
    assert "required" in schema
    assert "student_id" in schema["required"]
    assert "curriculum_path" in schema["required"]


@pytest.mark.asyncio
async def test_tool_execute_returns_workflow_id(db_session):
    """Execute should return workflow_id and results"""
    tool = AnalyzeStudentWeaknessesTool(db_session=db_session)
    
    arguments = {
        "student_id": "test_student_001",
        "curriculum_path": "중학수학.2학년.1학기",
        "include_weak_concepts": "true"
    }
    
    result = await tool.execute(arguments)
    
    assert isinstance(result, dict)
    assert "workflow_id" in result
    assert "weak_concepts" in result
    assert "questions" in result
    assert isinstance(result["weak_concepts"], list)
    assert isinstance(result["questions"], list)


@pytest.mark.asyncio
async def test_tool_execute_without_weak_concepts(db_session):
    """Execute with include_weak_concepts=false should return empty weak_concepts"""
    tool = AnalyzeStudentWeaknessesTool(db_session=db_session)
    
    arguments = {
        "student_id": "test_student_002",
        "curriculum_path": "중학수학.2학년.1학기",
        "include_weak_concepts": "false"
    }
    
    result = await tool.execute(arguments)
    
    assert result["weak_concepts"] == []
    assert len(result["questions"]) > 0
