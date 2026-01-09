from typing import List, Optional
from node0_student_hub.app.models.student import Student
from node0_student_hub.app.repositories.base import BaseRepository

class StudentRepository(BaseRepository[Student]):
    """
    Student Repository
    """
    
    async def get_by_school(self, school_id: str) -> List[Student]:
        return [s for s in self._mock_storage.values() if s.school_id == school_id]

    async def get_by_name(self, name: str) -> List[Student]:
        return [s for s in self._mock_storage.values() if name in s.name]
