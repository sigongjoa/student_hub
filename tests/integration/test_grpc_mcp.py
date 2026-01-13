"""
Integration Tests for gRPC MCP Server

gRPC MCP 서버의 통합 테스트 (pytest)
"""
import pytest
import grpc
import json

from generated import node0_mcp_pb2, node0_mcp_pb2_grpc


@pytest.fixture
async def grpc_channel():
    """gRPC channel fixture"""
    channel = grpc.aio.insecure_channel('localhost:50051')
    try:
        await channel.channel_ready()
        yield channel
    finally:
        await channel.close()


@pytest.fixture
def grpc_stub(grpc_channel):
    """gRPC stub fixture"""
    return node0_mcp_pb2_grpc.Node0MCPServiceStub(grpc_channel)


@pytest.mark.asyncio
async def test_health_check(grpc_stub):
    """Test HealthCheck RPC"""
    request = node0_mcp_pb2.HealthCheckRequest(service="node0_mcp")
    response = await grpc_stub.HealthCheck(request)

    assert response.status == "healthy"
    assert response.version == "1.0.0"
    assert response.metadata["tools_count"] == "5"
    assert response.metadata["service"] == "node0_mcp"


@pytest.mark.asyncio
async def test_list_tools_builtin_only(grpc_stub):
    """Test ListTools RPC with built-in tools only"""
    request = node0_mcp_pb2.ListToolsRequest(include_custom=False)
    response = await grpc_stub.ListTools(request)

    # Should have exactly 5 built-in tools
    assert len(response.tools) == 5

    # Check tool names
    tool_names = {tool.name for tool in response.tools}
    expected_tools = {
        "analyze_student_weaknesses",
        "create_error_review",
        "generate_learning_path",
        "prepare_exam",
        "get_student_profile"
    }
    assert tool_names == expected_tools

    # Check that all are not custom
    for tool in response.tools:
        assert tool.is_custom == False
        assert tool.name
        assert tool.description
        assert tool.input_schema
        assert tool.category in ["workflow", "query", "analysis"]


@pytest.mark.asyncio
async def test_list_tools_with_custom(grpc_stub):
    """Test ListTools RPC with custom tools included"""
    request = node0_mcp_pb2.ListToolsRequest(include_custom=True)

    try:
        response = await grpc_stub.ListTools(request)
        # Should have at least 5 built-in tools
        assert len(response.tools) >= 5
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            pytest.skip("Database not available")
        else:
            raise


@pytest.mark.asyncio
async def test_tool_schema_validity(grpc_stub):
    """Test that all tool schemas are valid JSON"""
    request = node0_mcp_pb2.ListToolsRequest(include_custom=False)
    response = await grpc_stub.ListTools(request)

    for tool in response.tools:
        # Should be valid JSON
        schema = json.loads(tool.input_schema)

        # Should have type object
        assert schema.get("type") == "object"

        # Should have properties
        assert "properties" in schema

        # Should have required fields (optional)
        if "required" in schema:
            assert isinstance(schema["required"], list)


@pytest.mark.asyncio
async def test_execute_tool_not_found(grpc_stub):
    """Test ExecuteTool with non-existent tool"""
    request = node0_mcp_pb2.ToolRequest(
        tool_name="nonexistent_tool",
        arguments={},
        session_id="test_session",
        user_id="test_user"
    )

    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await grpc_stub.ExecuteTool(request)

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    assert "not found" in exc_info.value.details().lower()


@pytest.mark.asyncio
async def test_execute_tool_validation_error(grpc_stub):
    """Test ExecuteTool with missing required arguments"""
    request = node0_mcp_pb2.ToolRequest(
        tool_name="get_student_profile",
        arguments={},  # Missing required student_id
        session_id="test_session",
        user_id="test_user"
    )

    response = await grpc_stub.ExecuteTool(request)

    # Should return error (not raise exception)
    assert response.success == False
    assert "student_id" in response.error.lower()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires database connection")
async def test_execute_tool_success(grpc_stub):
    """Test ExecuteTool with valid arguments"""
    request = node0_mcp_pb2.ToolRequest(
        tool_name="get_student_profile",
        arguments={
            "student_id": "student_test_001"
        },
        session_id="test_session",
        user_id="test_user"
    )

    response = await grpc_stub.ExecuteTool(request)

    assert response.success == True
    assert response.execution_time_ms > 0

    result = json.loads(response.result)
    assert "student" in result


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires database connection")
async def test_workflow_template_create(grpc_stub):
    """Test CreateWorkflowTemplate RPC"""
    template_def = {
        "nodes": [
            {
                "id": "node1",
                "type": "tool",
                "tool_name": "get_student_profile",
                "config": {
                    "student_id": "{{input.student_id}}"
                }
            }
        ],
        "edges": []
    }

    request = node0_mcp_pb2.CreateWorkflowTemplateRequest(
        name="Test Workflow",
        description="Test workflow template",
        definition=json.dumps(template_def),
        created_by="test_user",
        is_public=True
    )

    response = await grpc_stub.CreateWorkflowTemplate(request)

    assert response.id
    assert response.name == "Test Workflow"
    assert response.created_by == "test_user"
    assert response.is_public == True
    assert response.is_active == True


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires database connection")
async def test_workflow_execution_streaming(grpc_stub):
    """Test ExecuteWorkflowTemplate streaming RPC"""
    # First create a template
    template_def = {
        "nodes": [
            {
                "id": "node1",
                "type": "tool",
                "tool_name": "get_student_profile",
                "config": {
                    "student_id": "{{input.student_id}}"
                }
            }
        ],
        "edges": []
    }

    create_request = node0_mcp_pb2.CreateWorkflowTemplateRequest(
        name="Test Execution Workflow",
        description="Test",
        definition=json.dumps(template_def),
        created_by="test_user",
        is_public=True
    )

    create_response = await grpc_stub.CreateWorkflowTemplate(create_request)
    template_id = create_response.id

    # Execute workflow
    execute_request = node0_mcp_pb2.ExecuteWorkflowTemplateRequest(
        template_id=template_id,
        input_variables={
            "student_id": "student_test_001"
        },
        session_id="test_session",
        user_id="test_user"
    )

    events = []
    async for event in grpc_stub.ExecuteWorkflowTemplate(execute_request):
        events.append(event)

    # Should receive at least started and completed events
    assert len(events) >= 2

    event_types = [e.event_type for e in events]
    assert "started" in event_types
    assert "completed" in event_types or "error" in event_types


@pytest.mark.asyncio
async def test_concurrent_requests(grpc_stub):
    """Test concurrent gRPC requests"""
    import asyncio

    async def health_check():
        request = node0_mcp_pb2.HealthCheckRequest(service="node0_mcp")
        response = await grpc_stub.HealthCheck(request)
        return response.status

    async def list_tools():
        request = node0_mcp_pb2.ListToolsRequest(include_custom=False)
        response = await grpc_stub.ListTools(request)
        return len(response.tools)

    # Run 10 concurrent requests
    tasks = []
    for _ in range(5):
        tasks.append(health_check())
        tasks.append(list_tools())

    results = await asyncio.gather(*tasks)

    # All should succeed
    assert all(r == "healthy" or r == 5 for r in results)
