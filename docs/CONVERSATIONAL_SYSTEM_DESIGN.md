# Node 0 대화형 시스템 설계 문서

**버전**: 1.0.0
**작성일**: 2026-01-12
**상태**: Design Phase

---

## 📋 Executive Summary

Node 0 (Student Hub)를 **대화형 AI 플랫폼**으로 전환하여 선생님이 자연어로 학생 데이터를 조회하고 워크플로우를 실행할 수 있게 합니다.

### 핵심 목표

1. **대화형 인터페이스**: 채팅으로 "김철수의 약점 분석해줘" → 자동 워크플로우 실행
2. **워크플로우 템플릿 빌더**: n8n처럼 사용자가 커스텀 워크플로우를 만들 수 있음
3. **로컬 LLM 통합**: 비용 없이 프라이버시 보호하며 AI 기능 제공
4. **gRPC MCP Server**: Node 간 통신과 LLM tool use 지원
5. **반응형 디자인**: 모바일 + PC 모두 지원

---

## 🏗️ System Architecture

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Tailwind)               │
│  ┌──────────────────┬──────────────────────────────────┐   │
│  │   Dashboard      │       Chat Interface             │   │
│  │   - 차트/그래프  │       - 💬 대화창                │   │
│  │   - 테이블       │       - 📜 히스토리              │   │
│  │   - 필터         │       - 🔧 워크플로우 빌더       │   │
│  └──────────────────┴──────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/WebSocket (SSE for streaming)
┌───────────────────────▼─────────────────────────────────────┐
│                FastAPI Backend Server                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Chat API (/api/v1/chat)                            │   │
│  │  - Session management (Redis)                       │   │
│  │  - Conversation history (PostgreSQL)                │   │
│  │  - Streaming responses (SSE)                        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Workflow Template Manager                          │   │
│  │  - CRUD for custom workflows                        │   │
│  │  - Execution engine                                 │   │
│  │  - Template validation                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Agent Orchestrator                                 │   │
│  │  - Local LLM client (Ollama/vLLM)                   │   │
│  │  - Tool use coordination                            │   │
│  │  - Multi-step workflow execution                    │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ gRPC
┌───────────────────────▼─────────────────────────────────────┐
│             Node 0 MCP Server (gRPC)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MCP Tool Definitions                               │   │
│  │  - analyze_student_weaknesses                       │   │
│  │  - create_error_review                              │   │
│  │  - generate_learning_path                           │   │
│  │  - prepare_exam                                     │   │
│  │  - get_student_profile                              │   │
│  │  - [Custom Tools from Template Builder]            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Service Layer (기존 유지)                          │   │
│  │  - WeeklyDiagnosticService                          │   │
│  │  - ErrorReviewService                               │   │
│  │  - LearningPathService                              │   │
│  │  - ExamPrepService                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │ MCP (stdio/gRPC)
         ┌──────────────┼──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │ Node 1 │    │ Node 2 │    │ Node 4 │    │ Node 7 │
    │ Logic  │    │ Q-DNA  │    │ Lab    │    │ Error  │
    └────────┘    └────────┘    └────────┘    └────────┘
```

---

## 🎨 Frontend Design

### Tech Stack
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand (lightweight, 간단함)
- **Routing**: React Router v6
- **Charts**: Recharts (React-native charts)
- **Chat UI**: Custom components + react-markdown
- **Build**: Vite

### Layout Structure

```tsx
<AppLayout>
  <Sidebar>
    <Navigation />
    <UserProfile />
  </Sidebar>

  <MainContent>
    <Dashboard />  {/* 차트, 테이블, 필터 */}
  </MainContent>

  <ChatPanel>  {/* 우측 사이드바, 토글 가능 */}
    <ChatHeader>
      <Title>AI Assistant</Title>
      <WorkflowBuilder />  {/* 버튼 클릭 시 모달 */}
    </ChatHeader>
    <ChatMessages />
    <ChatInput />
  </ChatPanel>
</AppLayout>
```

### Responsive Design

**Desktop (>1024px)**:
```
┌──────────┬──────────────────┬────────────┐
│ Sidebar  │   Dashboard      │   Chat     │
│  (200px) │   (flex-grow)    │  (400px)   │
└──────────┴──────────────────┴────────────┘
```

**Tablet (768-1024px)**:
```
┌──────────┬──────────────────┐
│ Sidebar  │   Dashboard      │
│  (icon)  │   + Chat (tabs)  │
└──────────┴──────────────────┘
```

**Mobile (<768px)**:
```
┌───────────────────────┐
│   Bottom Nav          │
│   Dashboard (full)    │
│   or Chat (full)      │
└───────────────────────┘
```

### Chat Interface Components

```tsx
// ChatMessage.tsx
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    workflow_id?: string;
    tools_used?: string[];
    execution_time?: number;
  };
}

// ChatInput.tsx
<ChatInput
  onSend={handleSend}
  placeholder="학생 분석, 워크플로우 실행, 질문하기..."
  suggestions={[
    "김철수의 약점 개념 알려줘",
    "이번 주 진단 문제 10개 추천해줘",
    "3반 전체 위험군 학생 찾아줘"
  ]}
/>
```

---

## 🔧 Workflow Template Builder

### n8n-style Visual Builder

사용자가 **드래그 앤 드롭**으로 커스텀 워크플로우를 만들 수 있습니다.

#### Builder UI (React Flow)

```tsx
import ReactFlow from 'reactflow';

<WorkflowBuilder>
  <NodePalette>
    {/* 사용 가능한 노드들 */}
    <NodeType icon="🔍" name="학생 조회" />
    <NodeType icon="📊" name="숙련도 분석" />
    <NodeType icon="📝" name="문제 추천" />
    <NodeType icon="✉️" name="알림 전송" />
    <NodeType icon="🔁" name="조건 분기" />
  </NodePalette>

  <Canvas>
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
    />
  </Canvas>

  <NodeConfig>
    {/* 선택된 노드의 설정 */}
    <ConfigForm node={selectedNode} />
  </NodeConfig>
</WorkflowBuilder>
```

#### Workflow Template Schema

```typescript
interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  trigger: {
    type: 'manual' | 'chat_command' | 'schedule' | 'webhook';
    config: {
      command?: string;  // 예: "/분석 {student_id}"
      cron?: string;     // 예: "0 9 * * MON"
    };
  };
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  variables: Record<string, any>;
  created_by: string;
  created_at: Date;
  is_public: boolean;
}

interface WorkflowNode {
  id: string;
  type: 'mcp_tool' | 'condition' | 'transform' | 'notification';
  position: { x: number; y: number };
  data: {
    label: string;
    tool_name?: string;  // MCP tool name
    config: Record<string, any>;
  };
}

interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  condition?: string;  // 조건부 연결
}
```

#### Predefined Templates

```typescript
const BUILT_IN_TEMPLATES = [
  {
    name: "주간 약점 분석",
    command: "/주간분석 {student_id}",
    nodes: [
      { type: "get_student", config: { student_id: "$input.student_id" }},
      { type: "analyze_weaknesses", config: { days: 7 }},
      { type: "recommend_questions", config: { count: 10 }},
      { type: "send_notification", config: { recipient: "teacher" }}
    ]
  },
  {
    name: "시험 전 위험군 탐지",
    command: "/시험준비 {class_id} {exam_date}",
    nodes: [
      { type: "get_class_students", config: { class_id: "$input.class_id" }},
      { type: "analyze_risk", config: { threshold: 0.6 }},
      { type: "generate_learning_paths", config: { parallel: true }},
      { type: "create_report", config: { format: "pdf" }}
    ]
  }
];
```

#### Custom Tool Builder

사용자가 **새로운 MCP Tool**을 정의할 수 있습니다 (Low-code):

```typescript
interface CustomToolDefinition {
  name: string;
  description: string;
  input_schema: JSONSchema;
  steps: {
    action: 'call_mcp' | 'query_db' | 'transform' | 'aggregate';
    config: any;
  }[];
  output_schema: JSONSchema;
}

// 예시: "상위 10% 학생 찾기"
const customTool: CustomToolDefinition = {
  name: "find_top_students",
  description: "반에서 상위 10% 학생을 찾습니다",
  input_schema: {
    type: "object",
    properties: {
      class_id: { type: "string" },
      subject: { type: "string" }
    }
  },
  steps: [
    {
      action: "call_mcp",
      config: {
        node: "lab-node",
        tool: "get_class_students",
        params: { class_id: "$input.class_id" }
      }
    },
    {
      action: "aggregate",
      config: {
        field: "mastery_score",
        operation: "percentile",
        value: 90
      }
    }
  ],
  output_schema: {
    type: "object",
    properties: {
      students: { type: "array", items: { type: "object" }}
    }
  }
};
```

---

## 🚀 gRPC MCP Server

### Proto Definitions

```protobuf
// node0_mcp.proto
syntax = "proto3";

package node0;

service Node0MCPService {
  // Tool Execution
  rpc ExecuteTool(ToolRequest) returns (ToolResponse);

  // Tool Discovery
  rpc ListTools(ListToolsRequest) returns (ListToolsResponse);

  // Custom Tool Management
  rpc CreateCustomTool(CreateCustomToolRequest) returns (CustomTool);
  rpc GetCustomTool(GetCustomToolRequest) returns (CustomTool);
  rpc ListCustomTools(ListCustomToolsRequest) returns (ListCustomToolsResponse);

  // Workflow Template Management
  rpc CreateWorkflowTemplate(CreateWorkflowTemplateRequest) returns (WorkflowTemplate);
  rpc ExecuteWorkflowTemplate(ExecuteWorkflowTemplateRequest) returns (stream WorkflowExecutionEvent);
}

message ToolRequest {
  string tool_name = 1;
  map<string, string> arguments = 2;
  string session_id = 3;
}

message ToolResponse {
  bool success = 1;
  string result = 2;  // JSON serialized
  string error = 3;
  map<string, string> metadata = 4;
}

message Tool {
  string name = 1;
  string description = 2;
  string input_schema = 3;  // JSON schema
}

message ListToolsResponse {
  repeated Tool tools = 1;
}

message CustomTool {
  string id = 1;
  string name = 2;
  string description = 3;
  string input_schema = 4;
  string definition = 5;  // JSON serialized CustomToolDefinition
  string created_by = 6;
  int64 created_at = 7;
}

message WorkflowTemplate {
  string id = 1;
  string name = 2;
  string description = 3;
  string definition = 4;  // JSON serialized
  string created_by = 5;
  int64 created_at = 6;
}

message WorkflowExecutionEvent {
  string event_type = 1;  // started, node_completed, completed, error
  string node_id = 2;
  string data = 3;  // JSON serialized
}
```

### MCP Tool Definitions

```python
# app/mcp/tools.py
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class AnalyzeStudentWeaknessesTool(MCPTool):
    name = "analyze_student_weaknesses"
    description = "학생의 약점 개념을 분석하고 숙련도가 낮은 개념을 식별합니다"
    input_schema = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "학생 ID"
            },
            "curriculum_path": {
                "type": "string",
                "description": "커리큘럼 경로 (예: 중학수학.2학년.1학기)"
            },
            "include_weak_concepts": {
                "type": "boolean",
                "default": True
            }
        },
        "required": ["student_id", "curriculum_path"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from app.services.weekly_diagnostic_service import (
            WeeklyDiagnosticService,
            WeeklyDiagnosticRequest
        )
        from app.mcp.manager import MCPClientManager
        from app.db.session import get_db

        mcp = MCPClientManager()
        async with get_db() as db:
            service = WeeklyDiagnosticService(mcp, db)
            request = WeeklyDiagnosticRequest(
                student_id=arguments["student_id"],
                curriculum_path=arguments["curriculum_path"],
                include_weak_concepts=arguments.get("include_weak_concepts", True)
            )
            result = await service.start_diagnostic(request)

            return {
                "workflow_id": result.workflow_id,
                "weak_concepts": result.weak_concepts,
                "questions": [
                    {
                        "id": q.id,
                        "content": q.content,
                        "difficulty": q.difficulty
                    }
                    for q in result.questions
                ]
            }

# 다른 tools도 동일한 패턴으로 구현
class CreateErrorReviewTool(MCPTool):
    name = "create_error_review"
    # ...

class GenerateLearningPathTool(MCPTool):
    name = "generate_learning_path"
    # ...

class PrepareExamTool(MCPTool):
    name = "prepare_exam"
    # ...

class GetStudentProfileTool(MCPTool):
    name = "get_student_profile"
    # ...
```

### gRPC Service Implementation

```python
# app/grpc_services/mcp_service.py
import grpc
from generated import node0_mcp_pb2, node0_mcp_pb2_grpc
from app.mcp.tools import TOOL_REGISTRY
from app.mcp.custom_tools import CustomToolManager
from app.mcp.workflow_engine import WorkflowEngine
import json
import logging

logger = logging.getLogger(__name__)

class Node0MCPServicer(node0_mcp_pb2_grpc.Node0MCPServiceServicer):
    def __init__(self):
        self.custom_tool_manager = CustomToolManager()
        self.workflow_engine = WorkflowEngine()

    async def ExecuteTool(
        self,
        request: node0_mcp_pb2.ToolRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ToolResponse:
        """MCP Tool 실행"""
        try:
            tool_name = request.tool_name
            arguments = dict(request.arguments)

            # Built-in tool 찾기
            if tool_name in TOOL_REGISTRY:
                tool = TOOL_REGISTRY[tool_name]
                result = await tool.execute(arguments)

                return node0_mcp_pb2.ToolResponse(
                    success=True,
                    result=json.dumps(result),
                    metadata={"tool_type": "built_in"}
                )

            # Custom tool 찾기
            custom_tool = await self.custom_tool_manager.get_tool(tool_name)
            if custom_tool:
                result = await self.custom_tool_manager.execute_tool(
                    custom_tool,
                    arguments
                )

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
            logger.error(f"ExecuteTool failed: {e}")
            return node0_mcp_pb2.ToolResponse(
                success=False,
                error=str(e)
            )

    async def ListTools(
        self,
        request: node0_mcp_pb2.ListToolsRequest,
        context: grpc.aio.ServicerContext
    ) -> node0_mcp_pb2.ListToolsResponse:
        """사용 가능한 모든 Tool 목록"""
        tools = []

        # Built-in tools
        for name, tool in TOOL_REGISTRY.items():
            tools.append(node0_mcp_pb2.Tool(
                name=tool.name,
                description=tool.description,
                input_schema=json.dumps(tool.input_schema)
            ))

        # Custom tools
        custom_tools = await self.custom_tool_manager.list_tools()
        for custom_tool in custom_tools:
            tools.append(node0_mcp_pb2.Tool(
                name=custom_tool.name,
                description=custom_tool.description,
                input_schema=custom_tool.input_schema
            ))

        return node0_mcp_pb2.ListToolsResponse(tools=tools)

    async def ExecuteWorkflowTemplate(
        self,
        request: node0_mcp_pb2.ExecuteWorkflowTemplateRequest,
        context: grpc.aio.ServicerContext
    ):
        """워크플로우 템플릿 실행 (Streaming)"""
        template_id = request.template_id
        input_variables = dict(request.input_variables)

        async for event in self.workflow_engine.execute_template(
            template_id,
            input_variables
        ):
            yield node0_mcp_pb2.WorkflowExecutionEvent(
                event_type=event["type"],
                node_id=event.get("node_id", ""),
                data=json.dumps(event.get("data", {}))
            )
```

---

## 🤖 Local LLM + Agent Integration

### LLM Stack

**Option 1: Ollama (추천)**
```bash
# 설치
curl -fsSL https://ollama.com/install.sh | sh

# 모델 다운로드
ollama pull llama3.1:8b
ollama pull mistral:7b
```

**Option 2: vLLM (더 빠름, GPU 필요)**
```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-8B-Instruct
```

### Agent Orchestrator

```python
# app/agents/orchestrator.py
from typing import List, Dict, Any, AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
import json
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """로컬 LLM을 사용한 Agent Orchestrator"""

    def __init__(self, model_name: str = "llama3.1:8b"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0,
            base_url="http://localhost:11434"
        )
        self.tools: List[Tool] = []
        self.conversation_history: Dict[str, List] = {}

    def register_tool(self, tool: Tool):
        """MCP tool을 LangChain Tool로 등록"""
        self.tools.append(tool)

    async def chat(
        self,
        user_message: str,
        session_id: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """대화형 인터페이스"""

        # 대화 히스토리 가져오기
        history = self.conversation_history.get(session_id, [])

        # System prompt
        system_prompt = self._build_system_prompt()

        # Messages 구성
        messages = [
            SystemMessage(content=system_prompt),
            *history,
            HumanMessage(content=user_message)
        ]

        # LLM 호출 (streaming)
        if stream:
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content

                # Tool call 감지
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        yield f"\n\n🔧 실행 중: {tool_call['name']}\n"

                        # Tool 실행
                        result = await self._execute_tool(
                            tool_call['name'],
                            tool_call['args']
                        )

                        yield f"✅ 완료: {json.dumps(result, ensure_ascii=False)}\n\n"
        else:
            response = await self.llm.ainvoke(messages)
            yield response.content

        # 히스토리 업데이트
        history.append(HumanMessage(content=user_message))
        history.append(AIMessage(content=response.content))
        self.conversation_history[session_id] = history[-20:]  # 최근 20개만 유지

    def _build_system_prompt(self) -> str:
        """System prompt 생성 (tool 정보 포함)"""
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])

        return f"""당신은 학생 관리 시스템의 AI 어시스턴트입니다.
선생님이 학생 데이터를 조회하거나 분석할 때 도움을 줍니다.

사용 가능한 도구:
{tool_descriptions}

지침:
1. 선생님의 질문을 정확히 이해하고 적절한 도구를 선택하세요
2. 도구를 호출할 때는 필요한 매개변수를 정확히 전달하세요
3. 결과를 선생님이 이해하기 쉽게 설명하세요
4. 학생 이름이 주어지면 student_id로 변환하세요
5. 한국어로 대답하세요"""

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Tool 실행"""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        result = await tool.afunc(**arguments)
        return result
```

### Chat API Endpoint

```python
# app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json

from app.db.session import get_db
from app.agents.orchestrator import AgentOrchestrator
from app.models.conversation import Conversation, Message

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Global orchestrator (싱글톤)
orchestrator = AgentOrchestrator()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True

class ChatResponse(BaseModel):
    message: str
    session_id: str
    metadata: Optional[dict] = None

@router.post("/")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """대화형 채팅 엔드포인트"""

    # Session ID 생성 (없으면)
    session_id = request.session_id or str(uuid.uuid4())

    # Streaming 응답
    if request.stream:
        async def generate():
            async for chunk in orchestrator.chat(
                user_message=request.message,
                session_id=session_id,
                stream=True
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # 종료 신호
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    # Non-streaming 응답
    else:
        response_text = ""
        async for chunk in orchestrator.chat(
            user_message=request.message,
            session_id=session_id,
            stream=False
        ):
            response_text += chunk

        return ChatResponse(
            message=response_text,
            session_id=session_id
        )

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """대화 히스토리 조회"""
    # DB에서 조회
    conversation = await db.get(Conversation, session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation.messages
        ]
    }
```

---

## 📊 Data Models

### Conversation & Messages

```python
# app/models/conversation.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Conversation(Base):
    """대화 세션"""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # 선생님 ID
    title = Column(String(255), nullable=True)  # 자동 생성된 제목
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """대화 메시지"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)  # tool calls, execution time 등
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
```

### Workflow Templates

```python
# app/models/workflow_template.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class WorkflowTemplate(Base):
    """워크플로우 템플릿"""
    __tablename__ = "workflow_templates"

    id = Column(String, primary_key=True, default=lambda: f"wft_{uuid.uuid4().hex[:16]}")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # WorkflowTemplate schema
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # 실행 통계
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)

class CustomTool(Base):
    """커스텀 Tool 정의"""
    __tablename__ = "custom_tools"

    id = Column(String, primary_key=True, default=lambda: f"ct_{uuid.uuid4().hex[:16]}")
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    input_schema = Column(JSON, nullable=False)
    definition = Column(JSON, nullable=False)  # CustomToolDefinition schema
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
```

---

## 🔄 Data Flow Examples

### Example 1: 단순 질의

```
User: "김철수의 약점 개념 알려줘"
  ↓
Frontend (Chat Input)
  ↓ HTTP POST /api/v1/chat
Backend (FastAPI)
  ↓ AgentOrchestrator.chat()
Local LLM (Llama3.1)
  ↓ Tool call: analyze_student_weaknesses
gRPC MCP Server
  ↓ WeeklyDiagnosticService
Node 2 (Q-DNA) + Node 4 (Lab Node)
  ↓ MCP calls
Result
  ↓ Streaming response (SSE)
Frontend (Chat Messages)
  ↓
User: "김철수의 약점: 도함수(0.45), 극한(0.50)"
```

### Example 2: 커스텀 워크플로우 실행

```
User: "/시험준비 3반 2026-01-20"
  ↓
Frontend (Chat Input with command)
  ↓ HTTP POST /api/v1/chat
Backend (FastAPI)
  ↓ Command parser: 템플릿 "시험준비" 인식
WorkflowEngine.execute_template()
  ↓ Stream events
gRPC MCP Server
  ↓ Node 1: get_class_students(class_id="3반")
  ↓ Node 2: analyze_risk(students)
  ↓ Node 3: generate_learning_paths(at_risk_students)
  ↓ Node 4: create_report(format="pdf")
Result (Streaming)
  ↓ Event: started
  ↓ Event: node_completed (get_class_students)
  ↓ Event: node_completed (analyze_risk) - 5명 위험군
  ↓ Event: node_completed (generate_learning_paths)
  ↓ Event: completed
Frontend (Chat Messages)
  ↓
User: "✅ 3반 위험군 5명 탐지 완료. 맞춤형 학습 경로 생성됨. [다운로드 PDF]"
```

---

## 🛠️ Implementation Roadmap

### Phase 1: Backend Foundation (1-2주)

**Week 1: gRPC MCP Server**
- [ ] Proto 정의 작성 (`node0_mcp.proto`)
- [ ] gRPC service 구현
- [ ] Built-in MCP tools 구현 (5개)
- [ ] Tool registry 구현
- [ ] 단위 테스트

**Week 2: Chat API + LLM Integration**
- [ ] Ollama 설치 및 모델 다운로드
- [ ] AgentOrchestrator 구현
- [ ] Chat API endpoint 구현 (streaming)
- [ ] Conversation 모델 및 DB 마이그레이션
- [ ] Session management (Redis)

### Phase 2: Workflow Builder Backend (1주)

**Week 3: Template Engine**
- [ ] WorkflowTemplate 모델 및 DB 마이그레이션
- [ ] CustomTool 모델 및 DB 마이그레이션
- [ ] WorkflowEngine 구현 (실행 엔진)
- [ ] Custom tool manager 구현
- [ ] Template CRUD API

### Phase 3: Frontend (2주)

**Week 4: Base UI + Chat Interface**
- [ ] React + Vite 프로젝트 셋업
- [ ] Tailwind CSS + shadcn/ui 설정
- [ ] Layout 구조 (Sidebar + Dashboard + Chat)
- [ ] Chat 컴포넌트 구현
- [ ] SSE streaming 연결

**Week 5: Dashboard + Workflow Builder**
- [ ] Dashboard 컴포넌트 (차트, 테이블)
- [ ] React Flow 기반 워크플로우 빌더
- [ ] Template 관리 UI
- [ ] 반응형 디자인 (모바일 대응)

### Phase 4: Integration & Testing (1주)

**Week 6: E2E Integration**
- [ ] Frontend ↔ Backend 통합
- [ ] gRPC ↔ MCP 통합 테스트
- [ ] E2E 테스트 (Playwright)
- [ ] Performance 최적화
- [ ] 문서화

---

## 📁 Directory Structure

```
node0_student_hub/
├── frontend/                          # React 프론트엔드 (NEW)
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── ChatHistory.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── Charts.tsx
│   │   │   │   └── Tables.tsx
│   │   │   ├── workflow/
│   │   │   │   ├── WorkflowBuilder.tsx
│   │   │   │   ├── NodePalette.tsx
│   │   │   │   ├── Canvas.tsx
│   │   │   │   └── NodeConfig.tsx
│   │   │   └── layout/
│   │   │       ├── AppLayout.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Header.tsx
│   │   ├── stores/
│   │   │   ├── chatStore.ts
│   │   │   ├── workflowStore.ts
│   │   │   └── authStore.ts
│   │   ├── api/
│   │   │   ├── chatApi.ts
│   │   │   ├── workflowApi.ts
│   │   │   └── client.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── app/
│   ├── agents/                        # Agent Orchestrator (NEW)
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── tool_parser.py
│   │   └── prompt_templates.py
│   │
│   ├── mcp/                           # MCP Server (REFACTORED)
│   │   ├── __init__.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── weekly_diagnostic.py
│   │   │   ├── error_review.py
│   │   │   ├── learning_path.py
│   │   │   ├── exam_prep.py
│   │   │   └── student_profile.py
│   │   ├── custom_tools.py            # Custom tool manager
│   │   ├── workflow_engine.py         # Workflow execution engine
│   │   └── manager.py                 # MCP client manager (기존)
│   │
│   ├── grpc_services/                 # gRPC Services (NEW)
│   │   ├── __init__.py
│   │   ├── mcp_service.py             # Node0MCPServicer
│   │   └── health_service.py
│   │
│   ├── routers/
│   │   ├── chat.py                    # Chat API (NEW)
│   │   ├── workflows_template.py      # Template CRUD (NEW)
│   │   ├── workflows.py               # 기존 workflow endpoints
│   │   ├── mastery.py
│   │   └── attempts.py
│   │
│   ├── models/
│   │   ├── conversation.py            # NEW
│   │   ├── message.py                 # NEW
│   │   ├── workflow_template.py       # NEW
│   │   ├── custom_tool.py             # NEW
│   │   ├── student.py
│   │   ├── workflow_session.py
│   │   └── student_attempt.py
│   │
│   ├── services/                      # 기존 유지
│   │   ├── weekly_diagnostic_service.py
│   │   ├── error_review_service.py
│   │   ├── learning_path_service.py
│   │   └── exam_prep_service.py
│   │
│   └── api_app.py                     # FastAPI app
│
├── protos/                            # Protocol Buffers (NEW)
│   ├── node0_mcp.proto
│   └── common.proto
│
├── generated/                         # Generated gRPC code (NEW)
│   ├── __init__.py
│   ├── node0_mcp_pb2.py
│   └── node0_mcp_pb2_grpc.py
│
├── scripts/
│   ├── generate_proto.sh              # NEW
│   ├── start_ollama.sh                # NEW
│   └── test_mcp_connection.py
│
├── alembic/                           # DB migrations
│   └── versions/
│       ├── 20260112_add_conversations.py
│       └── 20260112_add_workflow_templates.py
│
├── tests/
│   ├── integration/
│   │   ├── test_chat_api.py           # NEW
│   │   ├── test_workflow_builder.py   # NEW
│   │   └── test_grpc_mcp.py           # NEW
│   └── unit/
│       ├── test_agent_orchestrator.py # NEW
│       └── test_workflow_engine.py    # NEW
│
├── docker-compose.yml                 # Ollama + Redis + PostgreSQL
├── requirements.txt
└── README.md
```

---

## 🔐 Security Considerations

1. **API Key Management**: 로컬 LLM 사용으로 외부 API key 불필요
2. **Rate Limiting**: FastAPI middleware로 DDoS 방지
3. **Input Validation**: Pydantic으로 모든 입력 검증
4. **RBAC**: 선생님 vs 관리자 권한 분리
5. **Audit Log**: 모든 workflow 실행 로그 저장

---

## 📈 Performance Optimization

1. **Caching**:
   - Redis로 대화 세션 캐싱
   - Tool 결과 캐싱 (TTL: 5분)

2. **Database Indexing**:
   - Conversation.user_id
   - Message.conversation_id
   - WorkflowTemplate.name

3. **Streaming**:
   - SSE로 LLM 응답 실시간 전송
   - Workflow 실행 진행상황 실시간 업데이트

4. **Connection Pooling**:
   - gRPC connection pool
   - Database connection pool

---

## 🎯 Success Metrics

1. **User Adoption**:
   - 일일 활성 선생님 수
   - 주간 대화 세션 수
   - 평균 세션 길이

2. **Workflow Performance**:
   - 평균 workflow 실행 시간
   - 성공률 (%)
   - Custom workflow 생성 수

3. **System Performance**:
   - API 응답 시간 (p95 < 500ms)
   - LLM 응답 시간 (streaming first token < 1s)
   - gRPC 호출 latency (p95 < 100ms)

---

## 📝 Next Steps

**당신이 선택해주세요**:

1. **프로토타입 먼저 구현** → Phase 1 시작 (gRPC MCP Server + Chat API)
2. **프론트엔드 mockup 먼저 보기** → React 컴포넌트 스케치
3. **워크플로우 빌더 상세 설계** → React Flow 아키텍처
4. **기타 질문이나 수정 요청**

어떤 방향으로 진행할까요?
