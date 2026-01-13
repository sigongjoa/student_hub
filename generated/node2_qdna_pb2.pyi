from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetStudentMasteryRequest(_message.Message):
    __slots__ = ("student_id", "concepts", "skill_ids")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    SKILL_IDS_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    concepts: _containers.RepeatedScalarFieldContainer[str]
    skill_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, student_id: _Optional[str] = ..., concepts: _Optional[_Iterable[str]] = ..., skill_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetStudentMasteryResponse(_message.Message):
    __slots__ = ("mastery",)
    class MasteryEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    MASTERY_FIELD_NUMBER: _ClassVar[int]
    mastery: _containers.ScalarMap[str, float]
    def __init__(self, mastery: _Optional[_Mapping[str, float]] = ...) -> None: ...

class RecommendQuestionsRequest(_message.Message):
    __slots__ = ("student_id", "concept", "difficulty", "count", "curriculum_path", "weak_concepts", "weak_ratio")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CURRICULUM_PATH_FIELD_NUMBER: _ClassVar[int]
    WEAK_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    WEAK_RATIO_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    concept: str
    difficulty: str
    count: int
    curriculum_path: str
    weak_concepts: _containers.RepeatedScalarFieldContainer[str]
    weak_ratio: float
    def __init__(self, student_id: _Optional[str] = ..., concept: _Optional[str] = ..., difficulty: _Optional[str] = ..., count: _Optional[int] = ..., curriculum_path: _Optional[str] = ..., weak_concepts: _Optional[_Iterable[str]] = ..., weak_ratio: _Optional[float] = ...) -> None: ...

class RecommendQuestionsResponse(_message.Message):
    __slots__ = ("questions", "student_id", "count")
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    questions: _containers.RepeatedCompositeFieldContainer[Question]
    student_id: str
    count: int
    def __init__(self, questions: _Optional[_Iterable[_Union[Question, _Mapping]]] = ..., student_id: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class Question(_message.Message):
    __slots__ = ("id", "content", "difficulty", "concepts", "estimated_time_minutes")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    id: str
    content: str
    difficulty: str
    concepts: _containers.RepeatedScalarFieldContainer[str]
    estimated_time_minutes: int
    def __init__(self, id: _Optional[str] = ..., content: _Optional[str] = ..., difficulty: _Optional[str] = ..., concepts: _Optional[_Iterable[str]] = ..., estimated_time_minutes: _Optional[int] = ...) -> None: ...

class GetQuestionDNARequest(_message.Message):
    __slots__ = ("question_id",)
    QUESTION_ID_FIELD_NUMBER: _ClassVar[int]
    question_id: str
    def __init__(self, question_id: _Optional[str] = ...) -> None: ...

class GetQuestionDNAResponse(_message.Message):
    __slots__ = ("question_id", "difficulty", "concepts", "bloom_level")
    QUESTION_ID_FIELD_NUMBER: _ClassVar[int]
    DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    BLOOM_LEVEL_FIELD_NUMBER: _ClassVar[int]
    question_id: str
    difficulty: str
    concepts: _containers.RepeatedScalarFieldContainer[str]
    bloom_level: str
    def __init__(self, question_id: _Optional[str] = ..., difficulty: _Optional[str] = ..., concepts: _Optional[_Iterable[str]] = ..., bloom_level: _Optional[str] = ...) -> None: ...

class EstimateLearningTimeRequest(_message.Message):
    __slots__ = ("concept", "current_mastery", "target_mastery")
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_MASTERY_FIELD_NUMBER: _ClassVar[int]
    TARGET_MASTERY_FIELD_NUMBER: _ClassVar[int]
    concept: str
    current_mastery: float
    target_mastery: float
    def __init__(self, concept: _Optional[str] = ..., current_mastery: _Optional[float] = ..., target_mastery: _Optional[float] = ...) -> None: ...

class EstimateLearningTimeResponse(_message.Message):
    __slots__ = ("concept", "estimated_hours", "current_mastery")
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_HOURS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_MASTERY_FIELD_NUMBER: _ClassVar[int]
    concept: str
    estimated_hours: int
    current_mastery: float
    def __init__(self, concept: _Optional[str] = ..., estimated_hours: _Optional[int] = ..., current_mastery: _Optional[float] = ...) -> None: ...
