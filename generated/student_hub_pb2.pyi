import workflows_pb2 as _workflows_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateStudentRequest(_message.Message):
    __slots__ = ("name", "grade", "school_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    GRADE_FIELD_NUMBER: _ClassVar[int]
    SCHOOL_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    grade: int
    school_id: str
    def __init__(self, name: _Optional[str] = ..., grade: _Optional[int] = ..., school_id: _Optional[str] = ...) -> None: ...

class StudentResponse(_message.Message):
    __slots__ = ("id", "name", "grade", "school_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    GRADE_FIELD_NUMBER: _ClassVar[int]
    SCHOOL_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    grade: int
    school_id: str
    created_at: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., grade: _Optional[int] = ..., school_id: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class GetStudentRequest(_message.Message):
    __slots__ = ("student_id",)
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    def __init__(self, student_id: _Optional[str] = ...) -> None: ...

class ListStudentsRequest(_message.Message):
    __slots__ = ("page", "page_size", "school_id")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SCHOOL_ID_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    school_id: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., school_id: _Optional[str] = ...) -> None: ...

class ListStudentsResponse(_message.Message):
    __slots__ = ("students", "total")
    STUDENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    students: _containers.RepeatedCompositeFieldContainer[StudentResponse]
    total: int
    def __init__(self, students: _Optional[_Iterable[_Union[StudentResponse, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class GetUnifiedProfileRequest(_message.Message):
    __slots__ = ("student_id",)
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    student_id: str
    def __init__(self, student_id: _Optional[str] = ...) -> None: ...

class UnifiedProfileResponse(_message.Message):
    __slots__ = ("student", "mastery", "activity", "error_notes")
    STUDENT_FIELD_NUMBER: _ClassVar[int]
    MASTERY_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_NOTES_FIELD_NUMBER: _ClassVar[int]
    student: StudentResponse
    mastery: _workflows_pb2.MasteryProfile
    activity: _workflows_pb2.ActivitySummary
    error_notes: _containers.RepeatedCompositeFieldContainer[_workflows_pb2.ErrorNote]
    def __init__(self, student: _Optional[_Union[StudentResponse, _Mapping]] = ..., mastery: _Optional[_Union[_workflows_pb2.MasteryProfile, _Mapping]] = ..., activity: _Optional[_Union[_workflows_pb2.ActivitySummary, _Mapping]] = ..., error_notes: _Optional[_Iterable[_Union[_workflows_pb2.ErrorNote, _Mapping]]] = ...) -> None: ...
