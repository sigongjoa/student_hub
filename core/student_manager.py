from typing import Dict, Any, Optional
from node0_student_hub.repositories.postgres_repo import PostgreSQLRepository
from node0_student_hub.models.schemas import Student

class StudentManager:
    def __init__(self, db: PostgreSQLRepository):
        self.db = db

    async def create_student(self, data: Dict[str, Any]) -> Student:
        student_id = await self.db.insert_student(data)
        # Fetch back to confirm and return Pydantic model
        saved_data = await self.db.get_student(student_id)
        if not saved_data:
            raise Exception("Failed to create student")
        return Student(**saved_data)

    async def get_student(self, student_id: str) -> Optional[Student]:
        data = await self.db.get_student(student_id)
        if data:
            return Student(**data)
        return None
