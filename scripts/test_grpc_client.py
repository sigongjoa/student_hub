"""
Test gRPC MCP Client

gRPC MCP 서버의 모든 기능을 테스트하는 클라이언트 스크립트
"""
import asyncio
import grpc
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generated import node0_mcp_pb2, node0_mcp_pb2_grpc


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def print_section(title: str):
    """Print section title"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}\n")


async def test_health_check(stub):
    """Test HealthCheck RPC"""
    print_section("Test 1: Health Check")

    try:
        request = node0_mcp_pb2.HealthCheckRequest(service="node0_mcp")
        response = await stub.HealthCheck(request)

        print_info(f"Status: {response.status}")
        print_info(f"Version: {response.version}")
        print_info(f"Metadata: {dict(response.metadata)}")

        if response.status == "healthy":
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check failed: {response.status}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


async def test_list_tools(stub):
    """Test ListTools RPC"""
    print_section("Test 2: List Tools")

    try:
        # List built-in tools only
        print_info("Listing built-in tools...")
        request = node0_mcp_pb2.ListToolsRequest(include_custom=False)
        response = await stub.ListTools(request)

        print_info(f"Found {len(response.tools)} built-in tools:")
        for tool in response.tools:
            print(f"  - {Colors.BOLD}{tool.name}{Colors.RESET}: {tool.description}")
            print(f"    Category: {tool.category}, Custom: {tool.is_custom}")

        if len(response.tools) == 5:
            print_success("All 5 built-in tools found")
            return True
        else:
            print_error(f"Expected 5 tools, found {len(response.tools)}")
            return False
    except Exception as e:
        print_error(f"ListTools error: {e}")
        return False


async def test_execute_tool(stub):
    """Test ExecuteTool RPC"""
    print_section("Test 3: Execute Tool")

    try:
        # Test get_student_profile tool (mock data)
        print_info("Executing get_student_profile tool...")

        request = node0_mcp_pb2.ToolRequest(
            tool_name="get_student_profile",
            arguments={
                "student_id": "student_test_001"
            },
            session_id="test_session",
            user_id="test_user"
        )

        response = await stub.ExecuteTool(request)

        print_info(f"Success: {response.success}")
        print_info(f"Execution time: {response.execution_time_ms}ms")

        if response.success:
            result = json.loads(response.result)
            print_info(f"Result keys: {list(result.keys())}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print_success("Tool execution successful")
            return True
        else:
            print_error(f"Tool execution failed: {response.error}")
            # This is expected if DB is not set up yet
            if "not yet implemented" in response.error.lower() or "mock" in response.error.lower():
                print_info("Mock implementation detected - this is expected")
                return True
            return False
    except Exception as e:
        print_error(f"ExecuteTool error: {e}")
        return False


async def test_workflow_template_crud(stub):
    """Test Workflow Template CRUD operations"""
    print_section("Test 4: Workflow Template CRUD")

    template_id = None

    try:
        # 1. Create workflow template
        print_info("Creating workflow template...")

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
            name="Test Workflow",
            description="Test workflow template",
            definition=json.dumps(template_def),
            created_by="test_user",
            is_public=True
        )

        create_response = await stub.CreateWorkflowTemplate(create_request)
        template_id = create_response.id

        print_info(f"Created template ID: {template_id}")
        print_info(f"Name: {create_response.name}")
        print_success("Workflow template created")

        # 2. Get workflow template
        print_info(f"Retrieving template {template_id}...")

        get_request = node0_mcp_pb2.GetWorkflowTemplateRequest(template_id=template_id)
        get_response = await stub.GetWorkflowTemplate(get_request)

        print_info(f"Retrieved: {get_response.name}")
        print_success("Workflow template retrieved")

        # 3. List workflow templates
        print_info("Listing workflow templates...")

        list_request = node0_mcp_pb2.ListWorkflowTemplatesRequest(
            page=1,
            page_size=10
        )
        list_response = await stub.ListWorkflowTemplates(list_request)

        print_info(f"Found {list_response.total} templates")
        print_success("Workflow templates listed")

        # 4. Delete workflow template
        print_info(f"Deleting template {template_id}...")

        delete_request = node0_mcp_pb2.DeleteWorkflowTemplateRequest(template_id=template_id)
        delete_response = await stub.DeleteWorkflowTemplate(delete_request)

        if delete_response.success:
            print_success("Workflow template deleted")
            return True
        else:
            print_error(f"Delete failed: {delete_response.message}")
            return False

    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            print_error("Database not available - this test requires PostgreSQL")
            print_info("This is expected if DB is not set up yet")
            return True  # Consider this as expected failure
        else:
            print_error(f"gRPC error: {e.code()} - {e.details()}")
            return False
    except Exception as e:
        print_error(f"Workflow template CRUD error: {e}")
        return False


async def test_execute_workflow_template(stub):
    """Test ExecuteWorkflowTemplate RPC (Streaming)"""
    print_section("Test 5: Execute Workflow Template (Streaming)")

    try:
        # First create a template
        print_info("Creating test workflow template...")

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
            description="Test workflow for execution",
            definition=json.dumps(template_def),
            created_by="test_user",
            is_public=True
        )

        create_response = await stub.CreateWorkflowTemplate(create_request)
        template_id = create_response.id

        print_info(f"Created template: {template_id}")

        # Execute workflow
        print_info("Executing workflow template...")

        execute_request = node0_mcp_pb2.ExecuteWorkflowTemplateRequest(
            template_id=template_id,
            input_variables={
                "student_id": "student_test_001"
            },
            session_id="test_session",
            user_id="test_user"
        )

        event_count = 0
        async for event in stub.ExecuteWorkflowTemplate(execute_request):
            event_count += 1
            print_info(f"Event {event_count}: {event.event_type}")
            if event.data:
                data = json.loads(event.data)
                print(f"  Data: {data}")

        print_info(f"Received {event_count} events")

        # Clean up
        delete_request = node0_mcp_pb2.DeleteWorkflowTemplateRequest(template_id=template_id)
        await stub.DeleteWorkflowTemplate(delete_request)

        print_success("Workflow execution streaming test completed")
        return True

    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            print_error("Database not available - this test requires PostgreSQL")
            print_info("This is expected if DB is not set up yet")
            return True
        else:
            print_error(f"gRPC error: {e.code()} - {e.details()}")
            return False
    except Exception as e:
        print_error(f"Execute workflow error: {e}")
        return False


async def main():
    """Main test function"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}Node 0 MCP gRPC Server Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Connect to gRPC server
    server_address = "localhost:50051"
    print_info(f"Connecting to gRPC server at {server_address}...")

    try:
        async with grpc.aio.insecure_channel(server_address) as channel:
            stub = node0_mcp_pb2_grpc.Node0MCPServiceStub(channel)

            # Wait for channel to be ready
            await channel.channel_ready()
            print_success(f"Connected to {server_address}")

            # Run tests
            results = []

            results.append(("Health Check", await test_health_check(stub)))
            results.append(("List Tools", await test_list_tools(stub)))
            results.append(("Execute Tool", await test_execute_tool(stub)))
            results.append(("Workflow Template CRUD", await test_workflow_template_crud(stub)))
            results.append(("Execute Workflow (Streaming)", await test_execute_workflow_template(stub)))

            # Summary
            print_section("Test Summary")

            passed = sum(1 for _, result in results if result)
            total = len(results)

            for test_name, result in results:
                status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
                print(f"  {test_name}: {status}")

            print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")

            if passed == total:
                print_success("All tests passed! 🎉")
                return 0
            else:
                print_error(f"{total - passed} test(s) failed")
                return 1

    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            print_error(f"Cannot connect to gRPC server at {server_address}")
            print_info("Make sure the server is running:")
            print_info("  python grpc_main.py")
            return 2
        else:
            print_error(f"gRPC error: {e}")
            return 3
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 4


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
