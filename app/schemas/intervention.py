from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class InterventionType(str, Enum):
    AUTO = "auto"
    TEACHER_REQUESTED = "teacher_requested"
    # Fallback/Custom types
    CONCEPT_REVIEW = "concept_review"
    DIFFICULTY_ADJUSTMENT = "difficulty_adjustment"

class InterventionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InterventionConfig(BaseModel):
    student_id: UUID4
    type: InterventionType = InterventionType.AUTO
    target_level: float = Field(0.8, ge=0.0, le=1.0)
    duration_days: int = 14
    focus_areas: Optional[List[str]] = None
    trigger: str = "manual" # Added for compatibility with test script
    reason: str = "Automated intervention" # Added for compatibility
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WeakArea(BaseModel):
    concept: str
    current_mastery: float
    target_mastery: float = 0.8
    priority: int = 1

class LearningStep(BaseModel):
    step: int
    activity: str
    concept: Optional[str] = None
    problem_set_id: Optional[str] = None
    params: Optional[Dict[str, Any]] = None # Added for flexibility
    estimated_duration: int = 600

class InterventionResponse(BaseModel):
    id: UUID4
    student_id: UUID4
    type: str # Changed to str to allow flexibility
    weak_areas: List[WeakArea] = [] # Made optional/default list
    learning_path: List[LearningStep] = []
    status: InterventionStatus
    progress: Dict[str, int]
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreateInterventionInput(InterventionConfig):
    pass
