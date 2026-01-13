"""
PrepareExamTool
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp.tools import MCPToolBase


class PrepareExamTool(MCPToolBase):
    name = "prepare_exam"
    description = "시험 준비를 위한 2주 학습 계획과 모의고사를 생성합니다"
    input_schema = {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "exam_date": {"type": "string"},
            "school_id": {"type": "string"},
            "curriculum_paths": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["student_id", "exam_date", "school_id"]
    }
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from app.mcp.manager import MCPClientManager
        
        mcp = MCPClientManager()
        await mcp.initialize()
        
        try:
            # Get exam scope
            scope = await mcp.call("school-info", "get_exam_scope", {
                "school_id": arguments["school_id"],
                "curriculum_paths": arguments.get("curriculum_paths", [])
            })
            
            # Get weak concepts
            weak = await mcp.call("lab-node", "get_weak_concepts", {
                "student_id": arguments["student_id"]
            })
            
            # Generate mock exam
            mock_exam = await mcp.call("q-metrics", "generate_mock_exam", {
                "student_id": arguments["student_id"],
                "scope": scope
            })
            
            return {
                "workflow_id": f"ep_{arguments['student_id']}",
                "focus_concepts": [w["concept"] for w in weak.get("weak_concepts", [])[:5]],
                "mock_exam_pdf_url": mock_exam.get("pdf_url", ""),
                "exam_date": arguments["exam_date"]
            }
        
        finally:
            await mcp.close_all()
