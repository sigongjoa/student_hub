import time
from datetime import datetime
from typing import Dict, Any, List
from node0_student_hub.repositories.postgres_repo import PostgreSQLRepository
from node0_student_hub.mcp_client.manager import MCPClientManager
from node0_student_hub.models.schemas import InterventionType

class InterventionEngine:
    def __init__(self, db: PostgreSQLRepository, mcp_manager: MCPClientManager):
        self.db = db
        self.mcp_manager = mcp_manager

    async def create_intervention(
        self,
        student_id: str,
        trigger: str,
        intervention_type: InterventionType,
        reason: str,
        metadata: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        
        intervention_id = f"int_{student_id}_{int(time.time())}"
        actions = []

        # 1. Define actions based on type
        if intervention_type == InterventionType.CONCEPT_REVIEW:
            weak_concepts = metadata.get("weak_concepts", [])
            
            # If no weak concepts provided, maybe fetch them via Logic Node?
            # For this simplified version, we assume they are passed or derive roughly
            if not weak_concepts:
                # Mock: call logic engine to find gaps if not provided
                gaps_result = await self.mcp_manager.call_tool("logic-engine-mcp", "find_concept_gap", {"student_id": student_id})
                weak_concepts = gaps_result.get("gaps", [])

            for concept in weak_concepts[:2]:
                video_action = {
                    "action_type": "send_video",
                    "params": {"concept_id": concept, "video_type": "review"},
                    "status": "pending"
                }
                actions.append(video_action)

                problem_action = {
                    "action_type": "generate_problems",
                    "params": {
                        "mcp_server": "gen-node-mcp",
                        "tool": "generate_picket_problem",
                        "tool_params": {
                            "student_id": student_id,
                            "target_concept": concept,
                            "difficulty_adjustment": -0.2
                        }
                    },
                    "status": "pending"
                }
                actions.append(problem_action)

        elif intervention_type == InterventionType.EASIER_PROBLEMS:
            current_concept = metadata.get("current_concept", "default_concept")
            action = {
                "action_type": "recommend_problems",
                "params": {
                    "mcp_server": "q-dna-mcp",
                    "tool": "find_similar_dna_problems",
                    "tool_params": {
                        "target_dna": current_concept,
                        "difficulty_range": [0.3, 0.5],
                        "limit": 10
                    }
                },
                "status": "pending"
            }
            actions.append(action)

        elif intervention_type == InterventionType.TEACHER_ALERT:
            action = {
                "action_type": "notify_teacher",
                "params": {
                    "student_id": student_id,
                    "alert_type": "struggling",
                    "message": reason,
                    "metadata": metadata
                },
                "status": "pending"
            }
            actions.append(action)

        # 2. Save to DB
        intervention_data = {
            "intervention_id": intervention_id,
            "student_id": student_id,
            "trigger": trigger,
            "intervention_type": intervention_type.value,
            "reason": reason,
            "metadata": metadata,
            "actions": actions,
            "created_at": datetime.now()
        }
        await self.db.insert_intervention(intervention_data)

        # 3. Execute actions (Mock async execution)
        # In real world: await execute_intervention_actions.delay(intervention_id, actions)
        
        return {
            "intervention_id": intervention_id,
            "student_id": student_id,
            "intervention_type": intervention_type.value,
            "actions": actions,
            "created_at": intervention_data["created_at"].isoformat(),
            "executed_at": None,
            "result": None
        }
