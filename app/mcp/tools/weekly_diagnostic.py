"""
AnalyzeStudentWeaknessesTool

Analyzes student weaknesses and recommends questions.
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp.tools import MCPToolBase


class AnalyzeStudentWeaknessesTool(MCPToolBase):
    """
    Tool for analyzing student weaknesses
    
    This tool:
    1. Gets recent learning concepts (from Node 4)
    2. Calculates BKT mastery (from Node 2)
    3. Identifies weak concepts (mastery < 0.6)
    4. Recommends questions (from Node 2)
    5. Creates workflow session in DB
    """
    
    name = "analyze_student_weaknesses"
    description = "학생의 약점 개념을 분석하고 숙련도가 낮은 개념을 식별하여 맞춤형 문제를 추천합니다"
    input_schema = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "학생 ID"
            },
            "curriculum_path": {
                "type": "string",
                "description": "커리큘럼 경로 (예: 중학수학.2학년.1학기)"
            },
            "include_weak_concepts": {
                "type": "boolean",
                "default": True,
                "description": "약점 개념 포함 여부"
            }
        },
        "required": ["student_id", "curriculum_path"]
    }
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weekly diagnostic workflow"""
        from app.services.weekly_diagnostic_service import (
            WeeklyDiagnosticService,
            WeeklyDiagnosticRequest
        )
        from app.mcp.manager import MCPClientManager
        
        # Convert string boolean to actual boolean
        include_weak = arguments.get("include_weak_concepts", "true")
        if isinstance(include_weak, str):
            include_weak = include_weak.lower() == "true"
        
        # Create MCP manager
        mcp = MCPClientManager()
        await mcp.initialize()
        
        try:
            # Create service with MCP manager and DB session
            service = WeeklyDiagnosticService(mcp, self.db_session)
            
            # Create request
            request = WeeklyDiagnosticRequest(
                student_id=arguments["student_id"],
                curriculum_path=arguments["curriculum_path"],
                include_weak_concepts=include_weak
            )
            
            # Execute diagnostic
            result = await service.start_diagnostic(request)
            
            # Return formatted result
            return {
                "workflow_id": result.workflow_id,
                "weak_concepts": result.weak_concepts,
                "questions": [
                    {
                        "id": q.id,
                        "content": q.content,
                        "difficulty": q.difficulty,
                        "concepts": q.concepts
                    }
                    for q in result.questions
                ],
                "total_estimated_time_minutes": result.total_estimated_time_minutes
            }
        
        finally:
            await mcp.close_all()
