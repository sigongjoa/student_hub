"""
CreateErrorReviewTool

Creates error review workflow with Anki scheduling.
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp.tools import MCPToolBase


class CreateErrorReviewTool(MCPToolBase):
    """Tool for creating error review and Anki schedule"""
    
    name = "create_error_review"
    description = "학생의 오답을 분석하고 Anki SM-2 알고리즘으로 복습 일정을 생성합니다"
    input_schema = {
        "type": "object",
        "properties": {
            "student_id": {"type": "string", "description": "학생 ID"},
            "question_id": {"type": "string", "description": "문제 ID"},
            "student_answer": {"type": "string", "description": "학생 답안"},
            "correct_answer": {"type": "string", "description": "정답"}
        },
        "required": ["student_id", "question_id", "student_answer", "correct_answer"]
    }
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute error review workflow"""
        from app.mcp.manager import MCPClientManager
        
        mcp = MCPClientManager()
        await mcp.initialize()
        
        try:
            # Call Node 7 (Error Note) to create error note
            error_note = await mcp.call("error-note", "create_error_note", {
                "student_id": arguments["student_id"],
                "question_id": arguments["question_id"],
                "student_answer": arguments["student_answer"],
                "correct_answer": arguments["correct_answer"]
            })
            
            # Calculate Anki schedule
            anki = await mcp.call("error-note", "calculate_anki_schedule", {
                "error_note_id": error_note["id"],
                "quality": 3  # Default medium quality
            })
            
            return {
                "error_note_id": error_note["id"],
                "next_review_date": anki["next_review_date"],
                "anki_interval_days": anki["interval_days"],
                "analysis": error_note.get("analysis", {})
            }
        
        finally:
            await mcp.close_all()
