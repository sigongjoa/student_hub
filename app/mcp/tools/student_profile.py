"""
GetStudentProfileTool
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp.tools import MCPToolBase


class GetStudentProfileTool(MCPToolBase):
    name = "get_student_profile"
    description = "학생의 통합 프로필 (정보, 숙련도, 활동, 오답노트)을 조회합니다"
    input_schema = {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"}
        },
        "required": ["student_id"]
    }
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from app.mcp.manager import MCPClientManager
        from app.repositories.student_repository import StudentRepository
        
        mcp = MCPClientManager()
        await mcp.initialize()
        
        try:
            # Get student from DB
            student_repo = StudentRepository(self.db_session)
            student = await student_repo.get_by_id(arguments["student_id"])
            
            if not student:
                return {"error": "Student not found"}
            
            # Get activity summary
            activity = await mcp.call("lab-node", "get_activity_summary", {
                "student_id": arguments["student_id"],
                "days": 30
            })
            
            # Get concept heatmap
            heatmap = await mcp.call("lab-node", "get_concept_heatmap", {
                "student_id": arguments["student_id"]
            })
            
            # Get error notes
            error_notes = await mcp.call("error-note", "list_error_notes_by_student", {
                "student_id": arguments["student_id"]
            })
            
            return {
                "student": {
                    "id": student.id,
                    "name": student.name,
                    "grade": student.grade,
                    "school_id": student.school_id
                },
                "activity": activity,
                "mastery": heatmap.get("heatmap", {}),
                "error_notes_count": len(error_notes.get("error_notes", []))
            }
        
        finally:
            await mcp.close_all()
