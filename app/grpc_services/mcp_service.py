"""
Node 0 MCP gRPC Service

LLM이 자연어로 워크플로우를 실행할 수 있도록 MCP tools를 제공하는 gRPC 서비스
"""
import grpc
import json
import logging
import time
from typing import Optional

from generated import node0_mcp_pb2, node0_mcp_pb2_grpc
from app.mcp.tools import TOOL_REGISTRY
from app.models.workflow_template import WorkflowTemplate as WorkflowTemplateModel
from app.models.custom_tool import CustomTool as CustomToolModel
from app.db.session import get_db_context
from sqlalchemy import select, delete

logger = logging.getLogger(__name__)


class Node0MCPServicer(node0_mcp_pb2_grpc.Node0MCPServiceServicer):
    """Node 0 MCP Service gRPC 구현"""

    def __init__(self):
        logger.info("Initializing Node0MCPServicer")

    # ============================================================================
    # Tool Execution
    # ============================================================================

    async def ExecuteTool(
        self,
        request: node0_mcp_pb2.ToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ToolResponse:
        """
        MCP Tool 실행

        Args:
            request: tool_name, arguments, session_id, user_id
            context: gRPC context

        Returns:
            ToolResponse with success, result, error, metadata
        """
        start_time = time.time()
        tool_name = request.tool_name
        arguments = dict(request.arguments)

        logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")

        try:
            # Built-in tool 찾기
            if tool_name in TOOL_REGISTRY:
                tool = TOOL_REGISTRY[tool_name]
                result_data = await tool.safe_execute(arguments)

                execution_time = int((time.time() - start_time) * 1000)

                if result_data["success"]:
                    return node0_mcp_pb2.ToolResponse(
                        success=True,
                        result=json.dumps(result_data["result"], ensure_ascii=False),
                        metadata={"tool_type": "built_in", "category": tool.category},
                        execution_time_ms=execution_time
                    )
                else:
                    return node0_mcp_pb2.ToolResponse(
                        success=False,
                        error=result_data["error"],
                        metadata={"tool_type": "built_in"},
                        execution_time_ms=execution_time
                    )

            # Custom tool 찾기
            async with get_db_context() as db:
                stmt = select(CustomToolModel).where(
                    CustomToolModel.name == tool_name,
                    CustomToolModel.is_active == True
                )
                result = await db.execute(stmt)
                custom_tool = result.scalar_one_or_none()

                if custom_tool:
                    # TODO: Execute custom tool
                    execution_time = int((time.time() - start_time) * 1000)
                    return node0_mcp_pb2.ToolResponse(
                        success=False,
                        error="Custom tool execution not yet implemented",
                        metadata={"tool_type": "custom"},
                        execution_time_ms=execution_time
                    )

            # Tool not found
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Tool '{tool_name}' not found"
            )

        except Exception as e:
            logger.error(f"ExecuteTool failed: {e}", exc_info=True)
            execution_time = int((time.time() - start_time) * 1000)
            return node0_mcp_pb2.ToolResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )

    # ============================================================================
    # Tool Discovery
    # ============================================================================

    async def ListTools(
        self,
        request: node0_mcp_pb2.ListToolsRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ListToolsResponse:
        """
        사용 가능한 모든 Tool 목록 조회

        Args:
            request: include_custom
            context: gRPC context

        Returns:
            ListToolsResponse with tools list
        """
        logger.info(f"Listing tools (include_custom={request.include_custom})")

        tools = []

        try:
            # Built-in tools
            for name, tool in TOOL_REGISTRY.items():
                tools.append(node0_mcp_pb2.Tool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=json.dumps(tool.input_schema, ensure_ascii=False),
                    category=tool.category,
                    is_custom=False
                ))

            # Custom tools
            if request.include_custom:
                async with get_db_context() as db:
                    stmt = select(CustomToolModel).where(CustomToolModel.is_active == True)
                    result = await db.execute(stmt)
                    custom_tools = result.scalars().all()

                    for custom_tool in custom_tools:
                        tools.append(node0_mcp_pb2.Tool(
                            name=custom_tool.name,
                            description=custom_tool.description,
                            input_schema=custom_tool.input_schema,
                            category="custom",
                            is_custom=True
                        ))

            logger.info(f"Found {len(tools)} tools")
            return node0_mcp_pb2.ListToolsResponse(tools=tools)

        except Exception as e:
            logger.error(f"ListTools failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    # ============================================================================
    # Custom Tool Management
    # ============================================================================

    async def CreateCustomTool(
        self,
        request: node0_mcp_pb2.CreateCustomToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.CustomTool:
        """커스텀 Tool 생성"""
        logger.info(f"Creating custom tool: {request.name}")

        try:
            async with get_db_context() as db:
                # Check if tool name already exists
                stmt = select(CustomToolModel).where(CustomToolModel.name == request.name)
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    await context.abort(
                        grpc.StatusCode.ALREADY_EXISTS,
                        f"Tool '{request.name}' already exists"
                    )

                # Create custom tool
                custom_tool = CustomToolModel(
                    name=request.name,
                    description=request.description,
                    input_schema=request.input_schema,
                    definition=request.definition,
                    created_by=request.created_by,
                    is_active=True
                )

                db.add(custom_tool)
                await db.commit()
                await db.refresh(custom_tool)

                logger.info(f"Created custom tool: {custom_tool.id}")

                return node0_mcp_pb2.CustomTool(
                    id=custom_tool.id,
                    name=custom_tool.name,
                    description=custom_tool.description,
                    input_schema=custom_tool.input_schema,
                    definition=custom_tool.definition,
                    created_by=custom_tool.created_by,
                    created_at=int(custom_tool.created_at.timestamp()),
                    is_active=custom_tool.is_active
                )

        except Exception as e:
            logger.error(f"CreateCustomTool failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetCustomTool(
        self,
        request: node0_mcp_pb2.GetCustomToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.CustomTool:
        """커스텀 Tool 조회"""
        logger.info(f"Getting custom tool: {request.tool_id}")

        try:
            async with get_db_context() as db:
                custom_tool = await db.get(CustomToolModel, request.tool_id)

                if not custom_tool:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"Custom tool '{request.tool_id}' not found"
                    )

                return node0_mcp_pb2.CustomTool(
                    id=custom_tool.id,
                    name=custom_tool.name,
                    description=custom_tool.description,
                    input_schema=custom_tool.input_schema,
                    definition=custom_tool.definition,
                    created_by=custom_tool.created_by,
                    created_at=int(custom_tool.created_at.timestamp()),
                    is_active=custom_tool.is_active
                )

        except Exception as e:
            logger.error(f"GetCustomTool failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ListCustomTools(
        self,
        request: node0_mcp_pb2.ListCustomToolsRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ListCustomToolsResponse:
        """커스텀 Tool 목록 조회"""
        logger.info(f"Listing custom tools (created_by={request.created_by})")

        try:
            async with get_db_context() as db:
                stmt = select(CustomToolModel).where(CustomToolModel.is_active == True)

                if request.created_by:
                    stmt = stmt.where(CustomToolModel.created_by == request.created_by)

                # Pagination
                page = request.page if request.page > 0 else 1
                page_size = request.page_size if request.page_size > 0 else 10
                stmt = stmt.offset((page - 1) * page_size).limit(page_size)

                result = await db.execute(stmt)
                custom_tools = result.scalars().all()

                # Get total count
                from sqlalchemy import func
                count_stmt = select(func.count()).select_from(CustomToolModel).where(
                    CustomToolModel.is_active == True
                )
                if request.created_by:
                    count_stmt = count_stmt.where(CustomToolModel.created_by == request.created_by)

                total_result = await db.execute(count_stmt)
                total = total_result.scalar()

                tools = [
                    node0_mcp_pb2.CustomTool(
                        id=tool.id,
                        name=tool.name,
                        description=tool.description,
                        input_schema=tool.input_schema,
                        definition=tool.definition,
                        created_by=tool.created_by,
                        created_at=int(tool.created_at.timestamp()),
                        is_active=tool.is_active
                    )
                    for tool in custom_tools
                ]

                return node0_mcp_pb2.ListCustomToolsResponse(
                    tools=tools,
                    total=total
                )

        except Exception as e:
            logger.error(f"ListCustomTools failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def DeleteCustomTool(
        self,
        request: node0_mcp_pb2.DeleteCustomToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.DeleteCustomToolResponse:
        """커스텀 Tool 삭제 (soft delete)"""
        logger.info(f"Deleting custom tool: {request.tool_id}")

        try:
            async with get_db_context() as db:
                custom_tool = await db.get(CustomToolModel, request.tool_id)

                if not custom_tool:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"Custom tool '{request.tool_id}' not found"
                    )

                # Soft delete
                custom_tool.is_active = False
                await db.commit()

                return node0_mcp_pb2.DeleteCustomToolResponse(
                    success=True,
                    message=f"Custom tool '{request.tool_id}' deleted successfully"
                )

        except Exception as e:
            logger.error(f"DeleteCustomTool failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    # ============================================================================
    # Workflow Template Management
    # ============================================================================

    async def CreateWorkflowTemplate(
        self,
        request: node0_mcp_pb2.CreateWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.WorkflowTemplate:
        """워크플로우 템플릿 생성"""
        logger.info(f"Creating workflow template: {request.name}")

        try:
            async with get_db_context() as db:
                template = WorkflowTemplateModel(
                    name=request.name,
                    description=request.description,
                    definition=json.loads(request.definition),
                    created_by=request.created_by,
                    is_public=request.is_public,
                    is_active=True
                )

                db.add(template)
                await db.commit()
                await db.refresh(template)

                logger.info(f"Created workflow template: {template.id}")

                return node0_mcp_pb2.WorkflowTemplate(
                    id=template.id,
                    name=template.name,
                    description=template.description or "",
                    definition=json.dumps(template.definition, ensure_ascii=False),
                    created_by=template.created_by,
                    created_at=int(template.created_at.timestamp()),
                    updated_at=int(template.updated_at.timestamp()) if template.updated_at else 0,
                    is_public=template.is_public,
                    is_active=template.is_active,
                    execution_count=template.execution_count or 0
                )

        except Exception as e:
            logger.error(f"CreateWorkflowTemplate failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetWorkflowTemplate(
        self,
        request: node0_mcp_pb2.GetWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.WorkflowTemplate:
        """워크플로우 템플릿 조회"""
        logger.info(f"Getting workflow template: {request.template_id}")

        try:
            async with get_db_context() as db:
                template = await db.get(WorkflowTemplateModel, request.template_id)

                if not template:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"Workflow template '{request.template_id}' not found"
                    )

                return node0_mcp_pb2.WorkflowTemplate(
                    id=template.id,
                    name=template.name,
                    description=template.description or "",
                    definition=json.dumps(template.definition, ensure_ascii=False),
                    created_by=template.created_by,
                    created_at=int(template.created_at.timestamp()),
                    updated_at=int(template.updated_at.timestamp()) if template.updated_at else 0,
                    is_public=template.is_public,
                    is_active=template.is_active,
                    execution_count=template.execution_count or 0
                )

        except Exception as e:
            logger.error(f"GetWorkflowTemplate failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ListWorkflowTemplates(
        self,
        request: node0_mcp_pb2.ListWorkflowTemplatesRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ListWorkflowTemplatesResponse:
        """워크플로우 템플릿 목록 조회"""
        logger.info(f"Listing workflow templates")

        try:
            async with get_db_context() as db:
                stmt = select(WorkflowTemplateModel).where(WorkflowTemplateModel.is_active == True)

                if request.created_by:
                    stmt = stmt.where(WorkflowTemplateModel.created_by == request.created_by)

                if request.only_public:
                    stmt = stmt.where(WorkflowTemplateModel.is_public == True)

                # Pagination
                page = request.page if request.page > 0 else 1
                page_size = request.page_size if request.page_size > 0 else 10
                stmt = stmt.offset((page - 1) * page_size).limit(page_size)

                result = await db.execute(stmt)
                templates = result.scalars().all()

                # Get total count
                from sqlalchemy import func
                count_stmt = select(func.count()).select_from(WorkflowTemplateModel).where(
                    WorkflowTemplateModel.is_active == True
                )
                if request.created_by:
                    count_stmt = count_stmt.where(WorkflowTemplateModel.created_by == request.created_by)
                if request.only_public:
                    count_stmt = count_stmt.where(WorkflowTemplateModel.is_public == True)

                total_result = await db.execute(count_stmt)
                total = total_result.scalar()

                template_list = [
                    node0_mcp_pb2.WorkflowTemplate(
                        id=tpl.id,
                        name=tpl.name,
                        description=tpl.description or "",
                        definition=json.dumps(tpl.definition, ensure_ascii=False),
                        created_by=tpl.created_by,
                        created_at=int(tpl.created_at.timestamp()),
                        updated_at=int(tpl.updated_at.timestamp()) if tpl.updated_at else 0,
                        is_public=tpl.is_public,
                        is_active=tpl.is_active,
                        execution_count=tpl.execution_count or 0
                    )
                    for tpl in templates
                ]

                return node0_mcp_pb2.ListWorkflowTemplatesResponse(
                    templates=template_list,
                    total=total
                )

        except Exception as e:
            logger.error(f"ListWorkflowTemplates failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def DeleteWorkflowTemplate(
        self,
        request: node0_mcp_pb2.DeleteWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.DeleteWorkflowTemplateResponse:
        """워크플로우 템플릿 삭제 (soft delete)"""
        logger.info(f"Deleting workflow template: {request.template_id}")

        try:
            async with get_db_context() as db:
                template = await db.get(WorkflowTemplateModel, request.template_id)

                if not template:
                    await context.abort(
                        grpc.StatusCode.NOT_FOUND,
                        f"Workflow template '{request.template_id}' not found"
                    )

                # Soft delete
                template.is_active = False
                await db.commit()

                return node0_mcp_pb2.DeleteWorkflowTemplateResponse(
                    success=True,
                    message=f"Workflow template '{request.template_id}' deleted successfully"
                )

        except Exception as e:
            logger.error(f"DeleteWorkflowTemplate failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    # ============================================================================
    # Workflow Execution
    # ============================================================================

    async def ExecuteWorkflowTemplate(
        self,
        request: node0_mcp_pb2.ExecuteWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ):
        """
        워크플로우 템플릿 실행 (Streaming)

        Args:
            request: template_id, input_variables, session_id, user_id
            context: gRPC context

        Yields:
            WorkflowExecutionEvent - started, node_started, node_completed, completed, error
        """
        logger.info(f"Executing workflow template: {request.template_id}")

        try:
            # Get template
            async with get_db_context() as db:
                template = await db.get(WorkflowTemplateModel, request.template_id)

                if not template:
                    yield node0_mcp_pb2.WorkflowExecutionEvent(
                        event_type="error",
                        node_id="",
                        node_name="",
                        data=json.dumps({"error": f"Template '{request.template_id}' not found"}),
                        timestamp=int(time.time())
                    )
                    return

            # TODO: Implement workflow execution engine
            # For now, just send placeholder events

            # Started event
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type="started",
                node_id="",
                node_name="",
                data=json.dumps({"template_id": request.template_id}),
                timestamp=int(time.time())
            )

            # Completed event
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type="completed",
                node_id="",
                node_name="",
                data=json.dumps({"result": "Workflow execution not yet implemented"}),
                timestamp=int(time.time())
            )

        except Exception as e:
            logger.error(f"ExecuteWorkflowTemplate failed: {e}", exc_info=True)
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type="error",
                node_id="",
                node_name="",
                data=json.dumps({"error": str(e)}),
                timestamp=int(time.time())
            )

    # ============================================================================
    # Health Check
    # ============================================================================

    async def HealthCheck(
        self,
        request: node0_mcp_pb2.HealthCheckRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.HealthCheckResponse:
        """Health check 엔드포인트"""
        logger.debug("Health check requested")

        try:
            # TODO: Check database connection
            # TODO: Check other dependencies

            return node0_mcp_pb2.HealthCheckResponse(
                status="healthy",
                version="1.0.0",
                metadata={
                    "tools_count": str(len(TOOL_REGISTRY)),
                    "service": "node0_mcp"
                }
            )

        except Exception as e:
            logger.error(f"HealthCheck failed: {e}", exc_info=True)
            return node0_mcp_pb2.HealthCheckResponse(
                status="unhealthy",
                version="1.0.0",
                metadata={"error": str(e)}
            )
