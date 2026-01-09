import asyncio
from typing import List, Dict, Any
from node0_student_hub.repositories.postgres_repo import PostgreSQLRepository
from node0_student_hub.mcp_client.manager import MCPClientManager

class ProfileAggregator:
    def __init__(self, db: PostgreSQLRepository, mcp_manager: MCPClientManager):
        self.db = db
        self.mcp_manager = mcp_manager

    async def get_unified_profile(
        self, 
        student_id: str, 
        include_sections: List[str] = ["basic", "mastery", "activities", "reports", "learning_path"],
        time_range: str = "last_30_days"
    ) -> Dict[str, Any]:
        profile = {}

        # 1. Basic Info (Node 0 DB)
        if "basic" in include_sections:
            student = await self.db.get_student(student_id)
            if student:
                profile["student_id"] = student.get("id")
                profile["name"] = student.get("name")
                profile["grade"] = student.get("grade")
                profile["school_code"] = student.get("school_code")
                # Handle datetime serialization if needed, assuming isoformat for now
                created_at = student.get("created_at")
                profile["created_at"] = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
            else:
                 # Handle case where student doesn't exist in local DB (maybe mock it for the test flow?)
                 # For now, let's just return what we have or empty
                 pass

        # 2. Mastery Data (Parallel Calls)
        if "mastery" in include_sections:
            mastery_task = self.mcp_manager.call_tool("q-dna-mcp", "get_student_mastery", {
                "student_id": student_id
            })
            heatmap_task = self.mcp_manager.call_tool("lab-node-mcp", "get_student_heatmap", {
                "student_id": student_id
            })

            mastery_result, heatmap_result = await asyncio.gather(mastery_task, heatmap_task)

            heatmap_data = heatmap_result.get("heatmap", {})
            profile["mastery_summary"] = {
                "average": mastery_result.get("average_mastery", 0.0),
                "strong_concepts": [c for c, m in heatmap_data.items() if m >= 0.8],
                "weak_concepts": [c for c, m in heatmap_data.items() if m < 0.5],
                "total_attempts": mastery_result.get("total_attempts", 0),
                "recent_trend": "stable" # Placeholder logic
            }
            profile["heatmap_data"] = heatmap_data

        # 3. Recent Activities (Node 4)
        if "activities" in include_sections:
            activities_result = await self.mcp_manager.call_tool("lab-node-mcp", "get_recent_activities", {
                "student_id": student_id,
                "time_range": time_range,
                "limit": 20
            })
            profile["recent_activities"] = activities_result.get("activities", [])
            profile["total_study_hours"] = activities_result.get("total_hours", 0.0)
            profile["last_active_date"] = activities_result.get("last_activity_date")

        # 4. Reports (Node 5) - Mocked repo call
        if "reports" in include_sections:
            reports = await self.db.get_student_reports(student_id, limit=5)
            profile["reports"] = reports
            profile["last_report_url"] = reports[0].get("pdf_url") if reports else None

        # 5. Learning Path (Node 0 DB)
        if "learning_path" in include_sections:
            learning_path = await self.db.get_active_learning_path(student_id)
            if learning_path:
                profile["learning_path"] = {
                    "current_stage": learning_path.get("current_stage"),
                    "next_milestone": learning_path.get("next_milestone"),
                    "progress_percentage": learning_path.get("progress", 0.0),
                    "estimated_completion_date": str(learning_path.get("estimated_completion"))
                }

        return profile
