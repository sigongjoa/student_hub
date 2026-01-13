"""
GenerateLearningPathTool
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp.tools import MCPToolBase


class GenerateLearningPathTool(MCPToolBase):
    name = "generate_learning_path"
    description = "학생의 목표 개념에 대한 개인화 학습 경로를 생성합니다 (선수지식 기반)"
    input_schema = {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "target_concept": {"type": "string"},
            "days": {"type": "integer", "default": 14}
        },
        "required": ["student_id", "target_concept"]
    }
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from app.mcp.manager import MCPClientManager
        
        mcp = MCPClientManager()
        await mcp.initialize()
        
        try:
            # Get concept heatmap
            heatmap = await mcp.call("lab-node", "get_concept_heatmap", {
                "student_id": arguments["student_id"]
            })
            
            # Get prerequisite graph
            graph = await mcp.call("logic-engine", "get_prerequisite_graph", {
                "concept": arguments["target_concept"]
            })
            
            # Estimate learning time
            time_est = await mcp.call("q-dna", "estimate_learning_time", {
                "concept": arguments["target_concept"],
                "current_mastery": heatmap["heatmap"].get(arguments["target_concept"], 0.5)
            })
            
            return {
                "workflow_id": f"lp_{arguments['student_id']}",
                "learning_path": [arguments["target_concept"]],
                "total_estimated_hours": time_est.get("estimated_hours", 10),
                "prerequisites": graph.get("graph", {}).get(arguments["target_concept"], {}).get("prerequisites", [])
            }
        
        finally:
            await mcp.close_all()
