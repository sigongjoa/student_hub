"""
Node 0 MCP Server

Provides 5 built-in educational workflow tools for LLM to call.
Port: 50051
"""
import grpc
import asyncio
import logging
from concurrent import futures
import json

from generated import node0_mcp_pb2, node0_mcp_pb2_grpc
from app.mcp.tool_registry import TOOL_CLASSES, get_tool_metadata
from app.db.session import get_db
from app.repositories.custom_tool_repository import CustomToolRepository
from app.repositories.workflow_template_repository import WorkflowTemplateRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Node0MCPServicer(node0_mcp_pb2_grpc.Node0MCPServiceServicer):
    """Node 0 MCP Service Implementation"""
    
    async def ExecuteTool(
        self,
        request: node0_mcp_pb2.ToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ToolResponse:
        """Execute a tool (built-in or custom)"""
        logger.info(f"ExecuteTool called: {request.tool_name}")
        
        try:
            tool_name = request.tool_name
            arguments = dict(request.arguments)
            
            # Check if it's a built-in tool
            if tool_name in TOOL_CLASSES:
                tool_class = TOOL_CLASSES[tool_name]
                
                # Get DB session
                async with get_db() as db:
                    tool_instance = tool_class(db_session=db)
                    result = await tool_instance.execute(arguments)
                
                return node0_mcp_pb2.ToolResponse(
                    success=True,
                    result=json.dumps(result, ensure_ascii=False),
                    metadata={"tool_type": "built_in"}
                )
            
            # Check if it's a custom tool
            async with get_db() as db:
                custom_tool_repo = CustomToolRepository(db)
                custom_tool = await custom_tool_repo.get_by_name(tool_name)
                
                if custom_tool:
                    # Execute custom tool (simplified for now)
                    result = {"message": "Custom tool execution not yet implemented"}
                    
                    return node0_mcp_pb2.ToolResponse(
                        success=True,
                        result=json.dumps(result),
                        metadata={"tool_type": "custom"}
                    )
            
            # Tool not found
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Tool '{tool_name}' not found"
            )
        
        except Exception as e:
            logger.error(f"ExecuteTool failed: {e}", exc_info=True)
            return node0_mcp_pb2.ToolResponse(
                success=False,
                error=str(e)
            )
    
    async def ListTools(
        self,
        request: node0_mcp_pb2.ListToolsRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ListToolsResponse:
        """List all available tools"""
        logger.info("ListTools called")
        
        try:
            tools = []
            
            # Get built-in tools
            tool_metadata = get_tool_metadata()
            for meta in tool_metadata:
                tools.append(node0_mcp_pb2.Tool(
                    name=meta["name"],
                    description=meta["description"],
                    input_schema=json.dumps(meta["input_schema"])
                ))
            
            # Get custom tools from DB
            async with get_db() as db:
                custom_tool_repo = CustomToolRepository(db)
                custom_tools = await custom_tool_repo.list_active_tools()
                
                for ct in custom_tools:
                    tools.append(node0_mcp_pb2.Tool(
                        name=ct.name,
                        description=ct.description,
                        input_schema=ct.input_schema
                    ))
            
            return node0_mcp_pb2.ListToolsResponse(tools=tools)
        
        except Exception as e:
            logger.error(f"ListTools failed: {e}", exc_info=True)
            return node0_mcp_pb2.ListToolsResponse(tools=[])
    
    async def CreateCustomTool(
        self,
        request: node0_mcp_pb2.CreateCustomToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.CustomTool:
        """Create a custom tool"""
        logger.info(f"CreateCustomTool called: {request.name}")
        
        try:
            async with get_db() as db:
                custom_tool_repo = CustomToolRepository(db)
                
                tool = await custom_tool_repo.create(
                    name=request.name,
                    description=request.description,
                    input_schema=request.input_schema,
                    definition=request.definition,
                    created_by=request.created_by
                )
                
                return node0_mcp_pb2.CustomTool(
                    id=tool.id,
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.input_schema,
                    definition=tool.definition,
                    created_by=tool.created_by,
                    created_at=int(tool.created_at.timestamp()),
                    is_active=tool.is_active
                )
        
        except Exception as e:
            logger.error(f"CreateCustomTool failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    async def GetCustomTool(
        self,
        request: node0_mcp_pb2.GetCustomToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.CustomTool:
        """Get a custom tool by ID"""
        logger.info(f"GetCustomTool called: {request.tool_id}")
        
        try:
            async with get_db() as db:
                custom_tool_repo = CustomToolRepository(db)
                tool = await custom_tool_repo.get_by_id(request.tool_id)
                
                if not tool:
                    await context.abort(grpc.StatusCode.NOT_FOUND, "Custom tool not found")
                
                return node0_mcp_pb2.CustomTool(
                    id=tool.id,
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.input_schema,
                    definition=tool.definition,
                    created_by=tool.created_by,
                    created_at=int(tool.created_at.timestamp()),
                    is_active=tool.is_active
                )
        
        except Exception as e:
            logger.error(f"GetCustomTool failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    async def ListCustomTools(
        self,
        request: node0_mcp_pb2.ListCustomToolsRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ListCustomToolsResponse:
        """List all custom tools"""
        logger.info("ListCustomTools called")
        
        try:
            async with get_db() as db:
                custom_tool_repo = CustomToolRepository(db)
                
                if request.include_inactive:
                    tools = await custom_tool_repo.list_all()
                else:
                    tools = await custom_tool_repo.list_active_tools()
                
                custom_tools = [
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
                    for tool in tools
                ]
                
                return node0_mcp_pb2.ListCustomToolsResponse(custom_tools=custom_tools)
        
        except Exception as e:
            logger.error(f"ListCustomTools failed: {e}", exc_info=True)
            return node0_mcp_pb2.ListCustomToolsResponse(custom_tools=[])
    
    async def CreateWorkflowTemplate(
        self,
        request: node0_mcp_pb2.CreateWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.WorkflowTemplate:
        """Create a workflow template"""
        logger.info(f"CreateWorkflowTemplate called: {request.name}")
        
        try:
            async with get_db() as db:
                template_repo = WorkflowTemplateRepository(db)
                
                template = await template_repo.create(
                    name=request.name,
                    description=request.description,
                    definition=request.definition,
                    created_by=request.created_by
                )
                
                return node0_mcp_pb2.WorkflowTemplate(
                    id=template.id,
                    name=template.name,
                    description=template.description,
                    definition=template.definition,
                    created_by=template.created_by,
                    created_at=int(template.created_at.timestamp()),
                    is_public=template.is_public,
                    is_active=template.is_active
                )
        
        except Exception as e:
            logger.error(f"CreateWorkflowTemplate failed: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    async def ExecuteWorkflowTemplate(
        self,
        request: node0_mcp_pb2.ExecuteWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ):
        """Execute a workflow template (streaming)"""
        logger.info(f"ExecuteWorkflowTemplate called: {request.template_id}")
        
        try:
            # Simplified workflow execution for now
            import time
            
            # Send started event
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type="started",
                node_id="",
                data=json.dumps({"template_id": request.template_id}),
                timestamp=int(time.time())
            )
            
            # Simulate workflow execution
            await asyncio.sleep(0.5)
            
            # Send completed event
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type="completed",
                node_id="",
                data=json.dumps({"result": "Workflow execution not yet fully implemented"}),
                timestamp=int(time.time())
            )
        
        except Exception as e:
            logger.error(f"ExecuteWorkflowTemplate failed: {e}", exc_info=True)
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type="error",
                node_id="",
                data=json.dumps({"error": str(e)}),
                timestamp=int(time.time())
            )


async def serve():
    """Start Node 0 gRPC MCP Server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    node0_mcp_pb2_grpc.add_Node0MCPServiceServicer_to_server(Node0MCPServicer(), server)
    
    server.add_insecure_port('[::]:50051')
    logger.info("🚀 Node 0 MCP Server starting on port 50051...")
    await server.start()
    logger.info("✅ Node 0 MCP Server started successfully!")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
