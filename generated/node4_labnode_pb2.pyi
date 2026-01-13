from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRecentConceptsRequest(_message.Message):
    __slots__ = ("student_id", "days", "curriculum_path")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    CURRICULUM_PATH_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    days: int
    curriculum_path: str
    def __init__(self, student_id: _Optional[str] = ..., days: _Optional[int] = ..., curriculum_path: _Optional[str] = ...) -> None: ...

class GetRecentConceptsResponse(_message.Message):
    __slots__ = ("concepts", "student_id", "period_days")
    CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    PERIOD_DAYS_FIELD_NUMBER: _ClassVar[int]
    concepts: _containers.RepeatedScalarFieldContainer[str]
    student_id: str
    period_days: int
    def __init__(self, concepts: _Optional[_Iterable[str]] = ..., student_id: _Optional[str] = ..., period_days: _Optional[int] = ...) -> None: ...

class GetConceptHeatmapRequest(_message.Message):
    __slots__ = ("student_id", "curriculum_path")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRICULUM_PATH_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    curriculum_path: str
    def __init__(self, student_id: _Optional[str] = ..., curriculum_path: _Optional[str] = ...) -> None: ...

class GetConceptHeatmapResponse(_message.Message):
    __slots__ = ("student_id", "heatmap", "timestamp")
    class HeatmapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    HEATMAP_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    heatmap: _containers.ScalarMap[str, float]
    timestamp: str
    def __init__(self, student_id: _Optional[str] = ..., heatmap: _Optional[_Mapping[str, float]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetWeakConceptsRequest(_message.Message):
    __slots__ = ("student_id", "threshold", "limit")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    threshold: float
    limit: int
    def __init__(self, student_id: _Optional[str] = ..., threshold: _Optional[float] = ..., limit: _Optional[int] = ...) -> None: ...

class GetWeakConceptsResponse(_message.Message):
    __slots__ = ("weak_concepts",)
    WEAK_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    weak_concepts: _containers.RepeatedCompositeFieldContainer[WeakConcept]
    def __init__(self, weak_concepts: _Optional[_Iterable[_Union[WeakConcept, _Mapping]]] = ...) -> None: ...

class WeakConcept(_message.Message):
    __slots__ = ("concept", "accuracy", "attempts")
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    concept: str
    accuracy: float
    attempts: int
    def __init__(self, concept: _Optional[str] = ..., accuracy: _Optional[float] = ..., attempts: _Optional[int] = ...) -> None: ...

class GetActivitySummaryRequest(_message.Message):
    __slots__ = ("student_id", "days")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    days: int
    def __init__(self, student_id: _Optional[str] = ..., days: _Optional[int] = ...) -> None: ...

class GetActivitySummaryResponse(_message.Message):
    __slots__ = ("student_id", "period_days", "total_attempts", "average_accuracy", "concepts_practiced", "last_activity", "timestamp")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    PERIOD_DAYS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ACCURACY_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_PRACTICED_FIELD_NUMBER: _ClassVar[int]
    LAST_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    period_days: int
    total_attempts: int
    average_accuracy: float
    concepts_practiced: int
    last_activity: str
    timestamp: str
    def __init__(self, student_id: _Optional[str] = ..., period_days: _Optional[int] = ..., total_attempts: _Optional[int] = ..., average_accuracy: _Optional[float] = ..., concepts_practiced: _Optional[int] = ..., last_activity: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetClassAnalyticsRequest(_message.Message):
    __slots__ = ("class_id", "start_date", "end_date")
    CLASS_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    class_id: str
    start_date: str
    end_date: str
    def __init__(self, class_id: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class GetClassAnalyticsResponse(_message.Message):
    __slots__ = ("total_students", "active_students", "average_accuracy", "at_risk_students", "common_weak_concepts")
    TOTAL_STUDENTS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_STUDENTS_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_ACCURACY_FIELD_NUMBER: _ClassVar[int]
    AT_RISK_STUDENTS_FIELD_NUMBER: _ClassVar[int]
    COMMON_WEAK_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    total_students: int
    active_students: int
    average_accuracy: float
    at_risk_students: int
    common_weak_concepts: _containers.RepeatedCompositeFieldContainer[CommonWeakConcept]
    def __init__(self, total_students: _Optional[int] = ..., active_students: _Optional[int] = ..., average_accuracy: _Optional[float] = ..., at_risk_students: _Optional[int] = ..., common_weak_concepts: _Optional[_Iterable[_Union[CommonWeakConcept, _Mapping]]] = ...) -> None: ...

class CommonWeakConcept(_message.Message):
    __slots__ = ("concept", "struggling_count")
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    STRUGGLING_COUNT_FIELD_NUMBER: _ClassVar[int]
    concept: str
    struggling_count: int
    def __init__(self, concept: _Optional[str] = ..., struggling_count: _Optional[int] = ...) -> None: ...
