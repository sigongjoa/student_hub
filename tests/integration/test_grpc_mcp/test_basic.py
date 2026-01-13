"""
Basic gRPC MCP Server Tests

기본적인 gRPC MCP 서버 기능 테스트
"""
import pytest
import grpc

from generated import node0_mcp_pb2, node0_mcp_pb2_grpc


@pytest.mark.asyncio
@pytest.mark.skip(reason="gRPC server needs to be running")
async def test_health_check():
    """Health check 테스트"""
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = node0_mcp_pb2_grpc.Node0MCPServiceStub(channel)

        request = node0_mcp_pb2.HealthCheckRequest(service="node0_mcp")
        response = await stub.HealthCheck(request)

        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert "tools_count" in response.metadata


@pytest.mark.asyncio
@pytest.mark.skip(reason="gRPC server needs to be running")
async def test_list_tools():
    """Tool 목록 조회 테스트"""
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = node0_mcp_pb2_grpc.Node0MCPServiceStub(channel)

        request = node0_mcp_pb2.ListToolsRequest(include_custom=False)
        response = await stub.ListTools(request)

        assert len(response.tools) == 5  # Built-in tools
        tool_names = [tool.name for tool in response.tools]

        assert "analyze_student_weaknesses" in tool_names
        assert "create_error_review" in tool_names
        assert "generate_learning_path" in tool_names
        assert "prepare_exam" in tool_names
        assert "get_student_profile" in tool_names


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires DB and MCP setup")
async def test_execute_tool_get_student_profile():
    """Tool 실행 테스트 - get_student_profile"""
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = node0_mcp_pb2_grpc.Node0MCPServiceStub(channel)

        request = node0_mcp_pb2.ToolRequest(
            tool_name="get_student_profile",
            arguments={"student_id": "student_test123"},
            session_id="test_session",
            user_id="test_teacher"
        )

        response = await stub.ExecuteTool(request)

        assert response.success is True
        assert response.result is not None
        assert response.execution_time_ms > 0
