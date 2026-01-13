from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WeeklyDiagnosticRequest(_message.Message):
    __slots__ = ("student_id", "curriculum_path", "include_weak_concepts")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRICULUM_PATH_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_WEAK_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    curriculum_path: str
    include_weak_concepts: bool
    def __init__(self, student_id: _Optional[str] = ..., curriculum_path: _Optional[str] = ..., include_weak_concepts: bool = ...) -> None: ...

class WeeklyDiagnosticResponse(_message.Message):
    __slots__ = ("workflow_id", "session_id", "questions", "weak_concepts", "total_estimated_time_minutes", "started_at")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    WEAK_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ESTIMATED_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    session_id: str
    questions: _containers.RepeatedCompositeFieldContainer[Question]
    weak_concepts: _containers.RepeatedScalarFieldContainer[str]
    total_estimated_time_minutes: int
    started_at: str
    def __init__(self, workflow_id: _Optional[str] = ..., session_id: _Optional[str] = ..., questions: _Optional[_Iterable[_Union[Question, _Mapping]]] = ..., weak_concepts: _Optional[_Iterable[str]] = ..., total_estimated_time_minutes: _Optional[int] = ..., started_at: _Optional[str] = ...) -> None: ...

class ErrorReviewRequest(_message.Message):
    __slots__ = ("student_id", "question_id", "student_answer", "correct_answer")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    QUESTION_ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ANSWER_FIELD_NUMBER: _ClassVar[int]
    CORRECT_ANSWER_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    question_id: str
    student_answer: str
    correct_answer: str
    def __init__(self, student_id: _Optional[str] = ..., question_id: _Optional[str] = ..., student_answer: _Optional[str] = ..., correct_answer: _Optional[str] = ...) -> None: ...

class ErrorReviewResponse(_message.Message):
    __slots__ = ("error_note_id", "next_review_date", "anki_interval_days", "analysis")
    ERROR_NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_REVIEW_DATE_FIELD_NUMBER: _ClassVar[int]
    ANKI_INTERVAL_DAYS_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    error_note_id: str
    next_review_date: str
    anki_interval_days: int
    analysis: ErrorAnalysis
    def __init__(self, error_note_id: _Optional[str] = ..., next_review_date: _Optional[str] = ..., anki_interval_days: _Optional[int] = ..., analysis: _Optional[_Union[ErrorAnalysis, _Mapping]] = ...) -> None: ...

class LearningPathRequest(_message.Message):
    __slots__ = ("student_id", "target_concept", "days")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_CONCEPT_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    target_concept: str
    days: int
    def __init__(self, student_id: _Optional[str] = ..., target_concept: _Optional[str] = ..., days: _Optional[int] = ...) -> None: ...

class LearningPathResponse(_message.Message):
    __slots__ = ("workflow_id", "learning_path", "total_estimated_hours", "daily_tasks")
    class DailyTasksEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    LEARNING_PATH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ESTIMATED_HOURS_FIELD_NUMBER: _ClassVar[int]
    DAILY_TASKS_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    learning_path: _containers.RepeatedCompositeFieldContainer[PathNode]
    total_estimated_hours: int
    daily_tasks: _containers.ScalarMap[str, int]
    def __init__(self, workflow_id: _Optional[str] = ..., learning_path: _Optional[_Iterable[_Union[PathNode, _Mapping]]] = ..., total_estimated_hours: _Optional[int] = ..., daily_tasks: _Optional[_Mapping[str, int]] = ...) -> None: ...

class ClassAnalyticsRequest(_message.Message):
    __slots__ = ("class_id", "start_date", "end_date")
    CLASS_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    class_id: str
    start_date: str
    end_date: str
    def __init__(self, class_id: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class ClassAnalyticsResponse(_message.Message):
    __slots__ = ("class_id", "summary", "at_risk_students", "common_weaknesses", "class_heatmap")
    CLASS_ID_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    AT_RISK_STUDENTS_FIELD_NUMBER: _ClassVar[int]
    COMMON_WEAKNESSES_FIELD_NUMBER: _ClassVar[int]
    CLASS_HEATMAP_FIELD_NUMBER: _ClassVar[int]
    class_id: str
    summary: ClassSummary
    at_risk_students: _containers.RepeatedCompositeFieldContainer[StudentRisk]
    common_weaknesses: _containers.RepeatedCompositeFieldContainer[ConceptGap]
    class_heatmap: Heatmap
    def __init__(self, class_id: _Optional[str] = ..., summary: _Optional[_Union[ClassSummary, _Mapping]] = ..., at_risk_students: _Optional[_Iterable[_Union[StudentRisk, _Mapping]]] = ..., common_weaknesses: _Optional[_Iterable[_Union[ConceptGap, _Mapping]]] = ..., class_heatmap: _Optional[_Union[Heatmap, _Mapping]] = ...) -> None: ...

class ExamPrepRequest(_message.Message):
    __slots__ = ("student_id", "exam_date", "school_id", "curriculum_paths")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    EXAM_DATE_FIELD_NUMBER: _ClassVar[int]
    SCHOOL_ID_FIELD_NUMBER: _ClassVar[int]
    CURRICULUM_PATHS_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    exam_date: str
    school_id: str
    curriculum_paths: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, student_id: _Optional[str] = ..., exam_date: _Optional[str] = ..., school_id: _Optional[str] = ..., curriculum_paths: _Optional[_Iterable[str]] = ...) -> None: ...

class ExamPrepResponse(_message.Message):
    __slots__ = ("workflow_id", "two_week_plan", "practice_problems", "focus_concepts", "mock_exam_pdf_url")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    TWO_WEEK_PLAN_FIELD_NUMBER: _ClassVar[int]
    PRACTICE_PROBLEMS_FIELD_NUMBER: _ClassVar[int]
    FOCUS_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    MOCK_EXAM_PDF_URL_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    two_week_plan: StudyPlan
    practice_problems: _containers.RepeatedCompositeFieldContainer[Question]
    focus_concepts: _containers.RepeatedScalarFieldContainer[str]
    mock_exam_pdf_url: str
    def __init__(self, workflow_id: _Optional[str] = ..., two_week_plan: _Optional[_Union[StudyPlan, _Mapping]] = ..., practice_problems: _Optional[_Iterable[_Union[Question, _Mapping]]] = ..., focus_concepts: _Optional[_Iterable[str]] = ..., mock_exam_pdf_url: _Optional[str] = ...) -> None: ...

class GetWorkflowStatusRequest(_message.Message):
    __slots__ = ("workflow_id",)
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    def __init__(self, workflow_id: _Optional[str] = ...) -> None: ...

class WorkflowStatusResponse(_message.Message):
    __slots__ = ("workflow_id", "status", "progress_percentage", "error_message", "completed_at")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    status: str
    progress_percentage: str
    error_message: str
    completed_at: str
    def __init__(self, workflow_id: _Optional[str] = ..., status: _Optional[str] = ..., progress_percentage: _Optional[str] = ..., error_message: _Optional[str] = ..., completed_at: _Optional[str] = ...) -> None: ...

class Question(_message.Message):
    __slots__ = ("id", "content", "difficulty", "concepts")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    content: str
    difficulty: str
    concepts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., content: _Optional[str] = ..., difficulty: _Optional[str] = ..., concepts: _Optional[_Iterable[str]] = ...) -> None: ...

class PathNode(_message.Message):
    __slots__ = ("concept", "order", "estimated_hours", "prerequisites")
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_HOURS_FIELD_NUMBER: _ClassVar[int]
    PREREQUISITES_FIELD_NUMBER: _ClassVar[int]
    concept: str
    order: int
    estimated_hours: int
    prerequisites: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, concept: _Optional[str] = ..., order: _Optional[int] = ..., estimated_hours: _Optional[int] = ..., prerequisites: _Optional[_Iterable[str]] = ...) -> None: ...

class ErrorAnalysis(_message.Message):
    __slots__ = ("misconception", "root_cause", "related_concepts")
    MISCONCEPTION_FIELD_NUMBER: _ClassVar[int]
    ROOT_CAUSE_FIELD_NUMBER: _ClassVar[int]
    RELATED_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    misconception: str
    root_cause: str
    related_concepts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, misconception: _Optional[str] = ..., root_cause: _Optional[str] = ..., related_concepts: _Optional[_Iterable[str]] = ...) -> None: ...

class ClassSummary(_message.Message):
    __slots__ = ("total_students", "average_accuracy", "active_students", "at_risk_count")
    TOTAL_STUDENTS_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ACCURACY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_STUDENTS_FIELD_NUMBER: _ClassVar[int]
    AT_RISK_COUNT_FIELD_NUMBER: _ClassVar[int]
    total_students: int
    average_accuracy: float
    active_students: int
    at_risk_count: int
    def __init__(self, total_students: _Optional[int] = ..., average_accuracy: _Optional[float] = ..., active_students: _Optional[int] = ..., at_risk_count: _Optional[int] = ...) -> None: ...

class StudentRisk(_message.Message):
    __slots__ = ("student_id", "name", "risk_score", "weak_concepts")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RISK_SCORE_FIELD_NUMBER: _ClassVar[int]
    WEAK_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    name: str
    risk_score: float
    weak_concepts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, student_id: _Optional[str] = ..., name: _Optional[str] = ..., risk_score: _Optional[float] = ..., weak_concepts: _Optional[_Iterable[str]] = ...) -> None: ...

class ConceptGap(_message.Message):
    __slots__ = ("concept", "class_average_accuracy", "struggling_count")
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    CLASS_AVERAGE_ACCURACY_FIELD_NUMBER: _ClassVar[int]
    STRUGGLING_COUNT_FIELD_NUMBER: _ClassVar[int]
    concept: str
    class_average_accuracy: float
    struggling_count: int
    def __init__(self, concept: _Optional[str] = ..., class_average_accuracy: _Optional[float] = ..., struggling_count: _Optional[int] = ...) -> None: ...

class Heatmap(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedCompositeFieldContainer[HeatmapCell]
    def __init__(self, cells: _Optional[_Iterable[_Union[HeatmapCell, _Mapping]]] = ...) -> None: ...

class HeatmapCell(_message.Message):
    __slots__ = ("concept_path", "accuracy", "attempts")
    CONCEPT_PATH_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    concept_path: str
    accuracy: float
    attempts: int
    def __init__(self, concept_path: _Optional[str] = ..., accuracy: _Optional[float] = ..., attempts: _Optional[int] = ...) -> None: ...

class StudyPlan(_message.Message):
    __slots__ = ("days",)
    DAYS_FIELD_NUMBER: _ClassVar[int]
    days: _containers.RepeatedCompositeFieldContainer[DailyTask]
    def __init__(self, days: _Optional[_Iterable[_Union[DailyTask, _Mapping]]] = ...) -> None: ...

class DailyTask(_message.Message):
    __slots__ = ("day_number", "date", "concepts_to_review", "practice_problems", "anki_reviews")
    DAY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_TO_REVIEW_FIELD_NUMBER: _ClassVar[int]
    PRACTICE_PROBLEMS_FIELD_NUMBER: _ClassVar[int]
    ANKI_REVIEWS_FIELD_NUMBER: _ClassVar[int]
    day_number: int
    date: str
    concepts_to_review: _containers.RepeatedScalarFieldContainer[str]
    practice_problems: _containers.RepeatedCompositeFieldContainer[Question]
    anki_reviews: int
    def __init__(self, day_number: _Optional[int] = ..., date: _Optional[str] = ..., concepts_to_review: _Optional[_Iterable[str]] = ..., practice_problems: _Optional[_Iterable[_Union[Question, _Mapping]]] = ..., anki_reviews: _Optional[int] = ...) -> None: ...

class MasteryProfile(_message.Message):
    __slots__ = ("concept_scores",)
    class ConceptScoresEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    CONCEPT_SCORES_FIELD_NUMBER: _ClassVar[int]
    concept_scores: _containers.ScalarMap[str, float]
    def __init__(self, concept_scores: _Optional[_Mapping[str, float]] = ...) -> None: ...

class ActivitySummary(_message.Message):
    __slots__ = ("total_attempts", "total_correct", "overall_accuracy", "active_days")
    TOTAL_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CORRECT_FIELD_NUMBER: _ClassVar[int]
    OVERALL_ACCURACY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_DAYS_FIELD_NUMBER: _ClassVar[int]
    total_attempts: int
    total_correct: int
    overall_accuracy: float
    active_days: int
    def __init__(self, total_attempts: _Optional[int] = ..., total_correct: _Optional[int] = ..., overall_accuracy: _Optional[float] = ..., active_days: _Optional[int] = ...) -> None: ...

class ErrorNote(_message.Message):
    __slots__ = ("id", "question_id", "created_at", "next_review")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUESTION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NEXT_REVIEW_FIELD_NUMBER: _ClassVar[int]
    id: str
    question_id: str
    created_at: str
    next_review: str
    def __init__(self, id: _Optional[str] = ..., question_id: _Optional[str] = ..., created_at: _Optional[str] = ..., next_review: _Optional[str] = ...) -> None: ...
