from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[ErrorCode]
    INVALID_ARGUMENT: _ClassVar[ErrorCode]
    NOT_FOUND: _ClassVar[ErrorCode]
    INTERNAL_ERROR: _ClassVar[ErrorCode]
    MCP_CALL_FAILED: _ClassVar[ErrorCode]
    DATABASE_ERROR: _ClassVar[ErrorCode]
OK: ErrorCode
INVALID_ARGUMENT: ErrorCode
NOT_FOUND: ErrorCode
INTERNAL_ERROR: ErrorCode
MCP_CALL_FAILED: ErrorCode
DATABASE_ERROR: ErrorCode

class Status(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: ErrorCode
    message: str
    def __init__(self, code: _Optional[_Union[ErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...
