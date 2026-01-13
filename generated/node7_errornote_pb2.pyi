from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateErrorNoteRequest(_message.Message):
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

class CreateErrorNoteResponse(_message.Message):
    __slots__ = ("id", "created_at", "analysis", "anki_data")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    ANKI_DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: str
    analysis: ErrorAnalysis
    anki_data: AnkiData
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[str] = ..., analysis: _Optional[_Union[ErrorAnalysis, _Mapping]] = ..., anki_data: _Optional[_Union[AnkiData, _Mapping]] = ...) -> None: ...

class ErrorAnalysis(_message.Message):
    __slots__ = ("misconception", "root_cause", "related_concepts")
    MISCONCEPTION_FIELD_NUMBER: _ClassVar[int]
    ROOT_CAUSE_FIELD_NUMBER: _ClassVar[int]
    RELATED_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    misconception: str
    root_cause: str
    related_concepts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, misconception: _Optional[str] = ..., root_cause: _Optional[str] = ..., related_concepts: _Optional[_Iterable[str]] = ...) -> None: ...

class AnkiData(_message.Message):
    __slots__ = ("ease_factor", "interval_days", "repetitions", "next_review")
    EASE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_DAYS_FIELD_NUMBER: _ClassVar[int]
    REPETITIONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_REVIEW_FIELD_NUMBER: _ClassVar[int]
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review: str
    def __init__(self, ease_factor: _Optional[float] = ..., interval_days: _Optional[int] = ..., repetitions: _Optional[int] = ..., next_review: _Optional[str] = ...) -> None: ...

class GetErrorNoteRequest(_message.Message):
    __slots__ = ("error_note_id",)
    ERROR_NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    error_note_id: str
    def __init__(self, error_note_id: _Optional[str] = ...) -> None: ...

class GetErrorNoteResponse(_message.Message):
    __slots__ = ("id", "student_id", "question_id", "student_answer", "correct_answer", "created_at", "analysis", "anki_data")
    ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    QUESTION_ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ANSWER_FIELD_NUMBER: _ClassVar[int]
    CORRECT_ANSWER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    ANKI_DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    student_id: str
    question_id: str
    student_answer: str
    correct_answer: str
    created_at: str
    analysis: ErrorAnalysis
    anki_data: AnkiData
    def __init__(self, id: _Optional[str] = ..., student_id: _Optional[str] = ..., question_id: _Optional[str] = ..., student_answer: _Optional[str] = ..., correct_answer: _Optional[str] = ..., created_at: _Optional[str] = ..., analysis: _Optional[_Union[ErrorAnalysis, _Mapping]] = ..., anki_data: _Optional[_Union[AnkiData, _Mapping]] = ...) -> None: ...

class ListErrorNotesByStudentRequest(_message.Message):
    __slots__ = ("student_id",)
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    def __init__(self, student_id: _Optional[str] = ...) -> None: ...

class ListErrorNotesByStudentResponse(_message.Message):
    __slots__ = ("error_notes",)
    ERROR_NOTES_FIELD_NUMBER: _ClassVar[int]
    error_notes: _containers.RepeatedCompositeFieldContainer[GetErrorNoteResponse]
    def __init__(self, error_notes: _Optional[_Iterable[_Union[GetErrorNoteResponse, _Mapping]]] = ...) -> None: ...

class CalculateAnkiScheduleRequest(_message.Message):
    __slots__ = ("error_note_id", "quality")
    ERROR_NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    error_note_id: str
    quality: int
    def __init__(self, error_note_id: _Optional[str] = ..., quality: _Optional[int] = ...) -> None: ...

class CalculateAnkiScheduleResponse(_message.Message):
    __slots__ = ("ease_factor", "interval_days", "next_review_date")
    EASE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_DAYS_FIELD_NUMBER: _ClassVar[int]
    NEXT_REVIEW_DATE_FIELD_NUMBER: _ClassVar[int]
    ease_factor: float
    interval_days: int
    next_review_date: str
    def __init__(self, ease_factor: _Optional[float] = ..., interval_days: _Optional[int] = ..., next_review_date: _Optional[str] = ...) -> None: ...

class GetDueReviewsRequest(_message.Message):
    __slots__ = ("student_id", "date")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    date: str
    def __init__(self, student_id: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class GetDueReviewsResponse(_message.Message):
    __slots__ = ("due_notes",)
    DUE_NOTES_FIELD_NUMBER: _ClassVar[int]
    due_notes: _containers.RepeatedCompositeFieldContainer[GetErrorNoteResponse]
    def __init__(self, due_notes: _Optional[_Iterable[_Union[GetErrorNoteResponse, _Mapping]]] = ...) -> None: ...

class DeleteErrorNoteRequest(_message.Message):
    __slots__ = ("error_note_id",)
    ERROR_NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    error_note_id: str
    def __init__(self, error_note_id: _Optional[str] = ...) -> None: ...

class DeleteErrorNoteResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
