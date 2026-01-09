from typing import Dict, Any, Optional
import asyncio
from node0_student_hub.app.repositories.student_repo import StudentRepository
from node0_student_hub.app.schemas.student import UnifiedProfile

# Mock MCP Client
class MCPClient:
    async def call(self, node: str, tool: str, params: dict) -> Dict:
        # Simulate network delay
        # await asyncio.sleep(0.1)
        
        if node == "q-dna" and tool == "get_mastery_level":
            return {"average": 0.75, "total_attempts": 150, "recent_trend": "increasing"}
        elif node == "lab-node" and tool == "get_recent_activities":
            return [
                {"date": "2024-03-20", "type": "problem_solving", "score": 85},
                {"date": "2024-03-19", "type": "video_watching", "score": 100}
            ]
        elif node == "lab-node" and tool == "get_student_heatmap":
             return {"Algebra": 0.8, "Geometry": 0.6}
        elif node == "report-node" and tool == "get_latest_reports":
            return [{"id": "rep_001", "date": "2024-03-01", "summary": "Good progress"}]
        return {}

class ProfileService:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo
        self.mcp = MCPClient()

    async def get_unified_profile(self, student_id: str, include_history: bool = False, days: int = 30) -> Dict[str, Any]:
        # 1. Get Master Data
        student = await self.student_repo.get_by_id(student_id)
        if not student:
             # If not found in repo, since we are mocking, allows creating a dummy one for test flow compatibility if needed, 
             # but better to rely on what was created.
             # raising Exception would be better in real app.
             return None

        # 2. Parallel Node Calls
        results = await self._aggregate_from_nodes(student_id, days)

        # 3. Merge
        profile = {
            "student_id": student.id,
            "name": student.name, # Helper for flat access
            "basic_info": {
                "name": student.name,
                "grade": student.grade,
                "school_code": student.school_id
            },
            "mastery_summary": results.get("mastery", {}),
            "heatmap_data": results.get("heatmap", {}),
            "recent_activities": results.get("activities", []),
            "latest_reports": results.get("reports", []),
            "generated_at": str(asyncio.get_event_loop().time()) # Placeholder
        }
        
        return profile

    async def _aggregate_from_nodes(self, student_id: str, days: int) -> Dict:
        # Mock parallel calls
        mastery_task = self.mcp.call("q-dna", "get_mastery_level", {"student_id": student_id})
        heatmap_task = self.mcp.call("lab-node", "get_student_heatmap", {"student_id": student_id})
        activities_task = self.mcp.call("lab-node", "get_recent_activities", {"student_id": student_id, "days": days})
        
        results = await asyncio.gather(mastery_task, heatmap_task, activities_task)
        
        return {
            "mastery": results[0],
            "heatmap": results[1],
            "activities": results[2],
            "reports": [] # Simple mock
        }
