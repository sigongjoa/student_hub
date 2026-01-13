from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ToolRequest(_message.Message):
    __slots__ = ("tool_name", "arguments", "session_id")
    class ArgumentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    tool_name: str
    arguments: _containers.ScalarMap[str, str]
    session_id: str
    def __init__(self, tool_name: _Optional[str] = ..., arguments: _Optional[_Mapping[str, str]] = ..., session_id: _Optional[str] = ...) -> None: ...

class ToolResponse(_message.Message):
    __slots__ = ("success", "result", "error", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    success: bool
    result: str
    error: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, success: bool = ..., result: _Optional[str] = ..., error: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ListToolsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListToolsResponse(_message.Message):
    __slots__ = ("tools",)
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    tools: _containers.RepeatedCompositeFieldContainer[Tool]
    def __init__(self, tools: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ("name", "description", "input_schema")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    input_schema: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., input_schema: _Optional[str] = ...) -> None: ...

class CreateCustomToolRequest(_message.Message):
    __slots__ = ("name", "description", "input_schema", "definition", "created_by")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    input_schema: str
    definition: str
    created_by: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., input_schema: _Optional[str] = ..., definition: _Optional[str] = ..., created_by: _Optional[str] = ...) -> None: ...

class GetCustomToolRequest(_message.Message):
    __slots__ = ("tool_id",)
    TOOL_ID_FIELD_NUMBER: _ClassVar[int]
    tool_id: str
    def __init__(self, tool_id: _Optional[str] = ...) -> None: ...

class ListCustomToolsRequest(_message.Message):
    __slots__ = ("include_inactive",)
    INCLUDE_INACTIVE_FIELD_NUMBER: _ClassVar[int]
    include_inactive: bool
    def __init__(self, include_inactive: bool = ...) -> None: ...

class ListCustomToolsResponse(_message.Message):
    __slots__ = ("custom_tools",)
    CUSTOM_TOOLS_FIELD_NUMBER: _ClassVar[int]
    custom_tools: _containers.RepeatedCompositeFieldContainer[CustomTool]
    def __init__(self, custom_tools: _Optional[_Iterable[_Union[CustomTool, _Mapping]]] = ...) -> None: ...

class CustomTool(_message.Message):
    __slots__ = ("id", "name", "description", "input_schema", "definition", "created_by", "created_at", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    input_schema: str
    definition: str
    created_by: str
    created_at: int
    is_active: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., input_schema: _Optional[str] = ..., definition: _Optional[str] = ..., created_by: _Optional[str] = ..., created_at: _Optional[int] = ..., is_active: bool = ...) -> None: ...

class CreateWorkflowTemplateRequest(_message.Message):
    __slots__ = ("name", "description", "definition", "created_by", "is_public")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    definition: str
    created_by: str
    is_public: bool
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., definition: _Optional[str] = ..., created_by: _Optional[str] = ..., is_public: bool = ...) -> None: ...

class ExecuteWorkflowTemplateRequest(_message.Message):
    __slots__ = ("template_id", "input_variables", "session_id")
    class InputVariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    template_id: str
    input_variables: _containers.ScalarMap[str, str]
    session_id: str
    def __init__(self, template_id: _Optional[str] = ..., input_variables: _Optional[_Mapping[str, str]] = ..., session_id: _Optional[str] = ...) -> None: ...

class WorkflowTemplate(_message.Message):
    __slots__ = ("id", "name", "description", "definition", "created_by", "created_at", "is_public", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    definition: str
    created_by: str
    created_at: int
    is_public: bool
    is_active: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., definition: _Optional[str] = ..., created_by: _Optional[str] = ..., created_at: _Optional[int] = ..., is_public: bool = ..., is_active: bool = ...) -> None: ...

class WorkflowExecutionEvent(_message.Message):
    __slots__ = ("event_type", "node_id", "data", "timestamp")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    node_id: str
    data: str
    timestamp: int
    def __init__(self, event_type: _Optional[str] = ..., node_id: _Optional[str] = ..., data: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...
