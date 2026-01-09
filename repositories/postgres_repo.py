from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

# In a real scenario, this would import sqlalchemy or asyncpg
# from node0_student_hub.models.schemas import Student, ...

class PostgreSQLRepository:
    def __init__(self):
        # In-memory storage for demonstration/testing without DB
        self._students = {}
        self._learning_paths = {}
        self._interventions = {}
        self._schedules = {}

    async def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        return self._students.get(student_id)

    async def insert_student(self, data: Dict[str, Any]) -> str:
        student_id = data.get("id")
        if not student_id:
            student_id = str(uuid.uuid4())
            data["id"] = student_id
        
        # Ensure dates are stored as objects or strings consistently
        if "created_at" not in data:
            data["created_at"] = datetime.now()
            
        self._students[student_id] = data
        return student_id

    async def get_active_learning_path(self, student_id: str) -> Optional[Dict[str, Any]]:
        # Return the first active path found
        for path in self._learning_paths.values():
            if path["student_id"] == student_id and path.get("is_active", True):
                return path
        return None

    async def insert_intervention(self, data: Dict[str, Any]) -> str:
        intervention_id = data.get("intervention_id")
        self._interventions[intervention_id] = data
        return intervention_id

    async def insert_schedule(self, data: Dict[str, Any]) -> str:
        schedule_id = data.get("schedule_id")
        self._schedules[schedule_id] = data
        return schedule_id

    async def get_student_reports(self, student_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Mocking relation for now since reports likely live in Node 5 or are linked here
        return []
