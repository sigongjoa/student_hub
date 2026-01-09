from typing import Dict, Any, List
from node0_student_hub.repositories.postgres_repo import PostgreSQLRepository
from node0_student_hub.mcp_client.manager import MCPClientManager
from node0_student_hub.core.profile_aggregator import ProfileAggregator
from node0_student_hub.core.intervention_engine import InterventionEngine
from node0_student_hub.core.student_manager import StudentManager
from node0_student_hub.models.schemas import (
    GetUnifiedProfileInput, CreateInterventionInput, SchedulePeriodicTaskInput,
    GetClassAnalyticsInput, CreateInterventionOutput, SchedulePeriodicTaskOutput,
    GetClassAnalyticsOutput
)

class StudentHubMCPServer:
    def __init__(self):
        self.db = PostgreSQLRepository()
        self.mcp_client = MCPClientManager()
        
        self.student_manager = StudentManager(self.db)
        self.profile_aggregator = ProfileAggregator(self.db, self.mcp_client)
        self.intervention_engine = InterventionEngine(self.db, self.mcp_client)

    async def get_unified_profile(self, input_data: GetUnifiedProfileInput) -> Dict[str, Any]:
        return await self.profile_aggregator.get_unified_profile(
            student_id=input_data.student_id,
            include_sections=input_data.include_sections,
            time_range=input_data.time_range
        )

    async def create_learning_intervention(self, input_data: CreateInterventionInput) -> CreateInterventionOutput:
        result = await self.intervention_engine.create_intervention(
            student_id=input_data.student_id,
            trigger=input_data.trigger,
            intervention_type=input_data.intervention_type,
            reason=input_data.reason,
            metadata=input_data.metadata
        )
        return CreateInterventionOutput(**result)

    async def schedule_periodic_task(self, input_data: SchedulePeriodicTaskInput) -> SchedulePeriodicTaskOutput:
        # Mock implementation for now
        import time
        from datetime import datetime
        schedule_id = f"sched_{input_data.student_id}_{int(time.time())}"
        
        # Save to DB mock
        schedule_data = {
            "schedule_id": schedule_id,
            "student_id": input_data.student_id,
            "task_type": input_data.task_type.value,
            "schedule": input_data.schedule,
            "next_run": datetime.now(), # Mock next run
            "enabled": input_data.enabled,
            "recipients": input_data.recipients,
            "params": input_data.params,
            "created_at": datetime.now()
        }
        await self.db.insert_schedule(schedule_data)

        return SchedulePeriodicTaskOutput(
            schedule_id=schedule_id,
            student_id=input_data.student_id,
            task_type=input_data.task_type,
            schedule=input_data.schedule,
            next_run=schedule_data["next_run"].isoformat(),
            enabled=input_data.enabled,
            created_at=schedule_data["created_at"].isoformat()
        )

    async def get_class_analytics(self, input_data: GetClassAnalyticsInput) -> GetClassAnalyticsOutput:
        # Mock analytics
        return GetClassAnalyticsOutput(
            scope=input_data.scope.value,
            scope_id=input_data.scope_id,
            student_count=30,
            average_mastery=0.72,
            completion_rate=0.85,
            weak_concepts=[
                {"concept_id": "math_101", "concept_name": "Calculus I", "average_mastery": 0.4, "struggling_student_count": 5}
            ]
        )
