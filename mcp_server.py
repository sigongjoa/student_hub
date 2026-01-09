from typing import Dict, Any, List
from node0_student_hub.app.repositories.student_repo import StudentRepository
from node0_student_hub.app.repositories.intervention_repo import InterventionRepository
from node0_student_hub.app.services.profile_service import ProfileService
from node0_student_hub.app.services.intervention_service import InterventionService
from node0_student_hub.app.models import Student, Intervention, LearningHistory
from node0_student_hub.app.schemas.profile import GetUnifiedProfileInput
from node0_student_hub.app.schemas.intervention import CreateInterventionInput

class StudentHubMCPServer:
    def __init__(self):
        # Initialize Repositories (Mock)
        self.student_repo = StudentRepository(Student)
        self.intervention_repo = InterventionRepository(Intervention)
        
        # Initialize Services
        self.profile_service = ProfileService(self.student_repo)
        self.intervention_service = InterventionService(self.student_repo, self.intervention_repo)
        
    # Wrapper for compatibility with Main.py / Test script
    async def get_unified_profile(self, input_data: GetUnifiedProfileInput) -> Dict[str, Any]:
        return await self.profile_service.get_unified_profile(
            student_id=str(input_data.student_id),
            include_history=input_data.include_history,
            days=input_data.days
        )

    async def create_learning_intervention(self, input_data: CreateInterventionInput):
        return await self.intervention_service.create_intervention(input_data)
        
    # Adapters for Student Manager calls to support legacy main.py usage
    class StudentManagerAdapter:
         def __init__(self, repo): self.repo = repo
         async def create_student(self, data): return await self.repo.create(data)
         async def get_student(self, id): return await self.repo.get_by_id(id)
    
    @property
    def student_manager(self):
        return self.StudentManagerAdapter(self.student_repo)

    @student_manager.setter
    def student_manager(self, value):
        pass # Ignore writes
