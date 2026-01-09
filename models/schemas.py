from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

# --- Enums ---

class InterventionType(str, Enum):
    CONCEPT_REVIEW = "concept_review"
    EASIER_PROBLEMS = "easier_problems"
    VIDEO_LESSON = "video_lesson"
    TEACHER_ALERT = "teacher_alert"
    ENCOURAGEMENT = "encouragement"

class TaskType(str, Enum):
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    LEARNING_PLAN_UPDATE = "learning_plan_update"
    INTERVENTION_CHECK = "intervention_check"

class AnalyticsScope(str, Enum):
    CLASS = "class"
    GRADE = "grade"
    SCHOOL = "school"

class AnalyticsMetric(str, Enum):
    AVERAGE_MASTERY = "average_mastery"
    COMPLETION_RATE = "completion_rate"
    WEAK_CONCEPTS = "weak_concepts"
    TOP_PERFORMERS = "top_performers"
    STRUGGLING_STUDENTS = "struggling_students"

# --- Common Models ---

class Student(BaseModel):
    id: str
    name: str
    grade: int
    school_code: str
    email: Optional[str] = None
    parent_email: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = {}

# --- MCP Tool Input/Outputs ---

# get_unified_profile
class GetUnifiedProfileInput(BaseModel):
    student_id: str = Field(..., description="Student ID")
    include_sections: List[str] = Field(
        default=["basic", "mastery", "activities", "reports", "learning_path"],
        description="Sections to include"
    )
    time_range: Optional[str] = Field(
        default="last_30_days",
        description="Time range for activity data"
    )

class MasterySummary(BaseModel):
    average: float
    strong_concepts: List[str]
    weak_concepts: List[str]
    total_attempts: int
    recent_trend: str

class LearningPathStatus(BaseModel):
    current_stage: str
    next_milestone: str
    progress_percentage: float
    estimated_completion_date: Optional[str]

class UnifiedProfile(BaseModel):
    student_id: str
    name: str
    grade: int
    school_code: str
    school_name: str
    created_at: str

    mastery_summary: Optional[MasterySummary] = None
    heatmap_data: Optional[Dict[str, float]] = None
    recent_activities: Optional[List[Dict[str, Any]]] = None
    total_study_hours: Optional[float] = None
    last_active_date: Optional[str] = None
    reports: Optional[List[Dict[str, Any]]] = None
    last_report_url: Optional[str] = None
    learning_path: Optional[LearningPathStatus] = None
    active_interventions: Optional[List[Dict[str, Any]]] = None
    intervention_history_count: Optional[int] = None

# create_learning_intervention
class CreateInterventionInput(BaseModel):
    student_id: str
    trigger: str = Field(..., description="Intervention trigger (auto/manual/scheduled)")
    intervention_type: InterventionType
    reason: str
    metadata: Dict[str, Any] = {}

class InterventionAction(BaseModel):
    action_type: str
    params: Dict[str, Any]
    scheduled_at: Optional[str] = None
    status: str

class CreateInterventionOutput(BaseModel):
    intervention_id: str
    student_id: str
    intervention_type: str
    actions: List[InterventionAction]
    created_at: str
    executed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

# schedule_periodic_task
class SchedulePeriodicTaskInput(BaseModel):
    student_id: str
    task_type: TaskType
    schedule: str
    enabled: bool = True
    recipients: List[str] = []
    params: Dict[str, Any] = {}

class SchedulePeriodicTaskOutput(BaseModel):
    schedule_id: str
    student_id: str
    task_type: str
    schedule: str
    next_run: str
    enabled: bool
    created_at: str

# get_class_analytics
class GetClassAnalyticsInput(BaseModel):
    scope: AnalyticsScope
    scope_id: str
    metrics: List[AnalyticsMetric] = [AnalyticsMetric.AVERAGE_MASTERY, AnalyticsMetric.WEAK_CONCEPTS]
    time_range: str = "last_30_days"

class StudentPerformance(BaseModel):
    student_id: str
    name: str
    average_mastery: float
    rank: int

class ConceptDistribution(BaseModel):
    concept_id: str
    concept_name: str
    average_mastery: float
    struggling_student_count: int

class GetClassAnalyticsOutput(BaseModel):
    scope: str
    scope_id: str
    student_count: int
    average_mastery: Optional[float] = None
    completion_rate: Optional[float] = None
    top_performers: Optional[List[StudentPerformance]] = None
    struggling_students: Optional[List[StudentPerformance]] = None
    weak_concepts: Optional[List[ConceptDistribution]] = None
    mastery_trend: Optional[List[Dict[str, Any]]] = None
