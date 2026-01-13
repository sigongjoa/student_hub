"""
WorkflowEngine Unit Tests

워크플로우 템플릿 실행 엔진 테스트
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.workflow_engine import WorkflowEngine, WorkflowNode, WorkflowEdge


class TestWorkflowEngine:
    """WorkflowEngine 테스트"""
    
    @pytest.mark.asyncio
    async def test_execute_single_node_workflow(self):
        """
        단일 노드 워크플로우 실행 테스트
        
        Given: 하나의 노드만 있는 워크플로우
        When: 워크플로우를 실행
        Then: 노드가 실행되고 결과 반환
        """
        # Given
        mock_tool = AsyncMock(return_value={"result": "success"})
        
        workflow = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "tool",
                    "tool_name": "test_tool",
                    "config": {"param": "value"}
                }
            ],
            "edges": []
        }
        
        engine = WorkflowEngine()
        engine.register_tool("test_tool", mock_tool)
        
        # When
        result = await engine.execute(workflow, {})
        
        # Then
        assert result["status"] == "completed"
        assert result["outputs"]["node1"]["result"] == "success"
        mock_tool.assert_called_once_with({"param": "value"})
    
    
    @pytest.mark.asyncio
    async def test_execute_sequential_workflow(self):
        """
        순차 실행 워크플로우 테스트
        
        Given: 2개 노드가 순차적으로 연결된 워크플로우
        When: 워크플로우를 실행
        Then: 노드가 순서대로 실행되고 데이터가 전달됨
        """
        # Given
        tool1 = AsyncMock(return_value={"data": "from_tool1"})
        tool2 = AsyncMock(return_value={"data": "from_tool2"})
        
        workflow = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "tool",
                    "tool_name": "tool1",
                    "config": {}
                },
                {
                    "id": "node2",
                    "type": "tool",
                    "tool_name": "tool2",
                    "config": {
                        "input": "{{node1.data}}"  # node1의 출력 참조
                    }
                }
            ],
            "edges": [
                {"from": "node1", "to": "node2"}
            ]
        }
        
        engine = WorkflowEngine()
        engine.register_tool("tool1", tool1)
        engine.register_tool("tool2", tool2)
        
        # When
        result = await engine.execute(workflow, {})
        
        # Then
        assert result["status"] == "completed"
        assert result["outputs"]["node1"]["data"] == "from_tool1"
        assert result["outputs"]["node2"]["data"] == "from_tool2"
        
        # node2가 node1의 출력을 받았는지 확인
        tool2_call_args = tool2.call_args[0][0]
        assert tool2_call_args["input"] == "from_tool1"
    
    
    @pytest.mark.asyncio
    async def test_execute_parallel_workflow(self):
        """
        병렬 실행 워크플로우 테스트
        
        Given: 2개 노드가 병렬로 실행되는 워크플로우
        When: 워크플로우를 실행
        Then: 두 노드가 동시에 실행됨
        """
        # Given
        tool1 = AsyncMock(return_value={"data": "tool1"})
        tool2 = AsyncMock(return_value={"data": "tool2"})
        
        workflow = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "tool",
                    "tool_name": "tool1",
                    "config": {}
                },
                {
                    "id": "node2",
                    "type": "tool",
                    "tool_name": "tool2",
                    "config": {}
                }
            ],
            "edges": []  # 엣지 없음 = 병렬 실행
        }
        
        engine = WorkflowEngine()
        engine.register_tool("tool1", tool1)
        engine.register_tool("tool2", tool2)
        
        # When
        result = await engine.execute(workflow, {})
        
        # Then
        assert result["status"] == "completed"
        assert result["outputs"]["node1"]["data"] == "tool1"
        assert result["outputs"]["node2"]["data"] == "tool2"
        assert tool1.called
        assert tool2.called
    
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_input_variables(self):
        """
        입력 변수를 사용하는 워크플로우 테스트
        
        Given: 입력 변수를 참조하는 워크플로우
        When: 입력 변수와 함께 실행
        Then: 입력 변수가 올바르게 전달됨
        """
        # Given
        tool = AsyncMock(return_value={"result": "ok"})
        
        workflow = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "tool",
                    "tool_name": "test_tool",
                    "config": {
                        "student_id": "{{input.student_id}}"
                    }
                }
            ],
            "edges": []
        }
        
        engine = WorkflowEngine()
        engine.register_tool("test_tool", tool)
        
        input_vars = {"student_id": "student_123"}
        
        # When
        result = await engine.execute(workflow, input_vars)
        
        # Then
        assert result["status"] == "completed"
        tool_call_args = tool.call_args[0][0]
        assert tool_call_args["student_id"] == "student_123"
    
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_error(self):
        """
        에러 발생 시 워크플로우 처리 테스트
        
        Given: 실행 중 에러가 발생하는 워크플로우
        When: 워크플로우를 실행
        Then: 에러가 캡처되고 적절한 상태 반환
        """
        # Given
        tool = AsyncMock(side_effect=Exception("Tool execution failed"))
        
        workflow = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "tool",
                    "tool_name": "failing_tool",
                    "config": {}
                }
            ],
            "edges": []
        }
        
        engine = WorkflowEngine()
        engine.register_tool("failing_tool", tool)
        
        # When
        result = await engine.execute(workflow, {})
        
        # Then
        assert result["status"] == "failed"
        assert "error" in result
        assert "Tool execution failed" in result["error"]
    
    
    @pytest.mark.asyncio
    async def test_execute_complex_workflow(self):
        """
        복잡한 워크플로우 테스트 (분기 + 병합)
        
        Given: 분기와 병합이 있는 복잡한 워크플로우
        When: 워크플로우를 실행
        Then: 올바른 실행 순서와 데이터 전달
        """
        # Given
        # node1 -> node2
        #       -> node3 -> node4
        tool1 = AsyncMock(return_value={"step": 1})
        tool2 = AsyncMock(return_value={"step": 2})
        tool3 = AsyncMock(return_value={"step": 3})
        tool4 = AsyncMock(return_value={"step": 4})
        
        workflow = {
            "nodes": [
                {"id": "node1", "type": "tool", "tool_name": "tool1", "config": {}},
                {"id": "node2", "type": "tool", "tool_name": "tool2", "config": {"from": "{{node1.step}}"}},
                {"id": "node3", "type": "tool", "tool_name": "tool3", "config": {"from": "{{node1.step}}"}},
                {"id": "node4", "type": "tool", "tool_name": "tool4", "config": {"from": "{{node3.step}}"}}
            ],
            "edges": [
                {"from": "node1", "to": "node2"},
                {"from": "node1", "to": "node3"},
                {"from": "node3", "to": "node4"}
            ]
        }
        
        engine = WorkflowEngine()
        engine.register_tool("tool1", tool1)
        engine.register_tool("tool2", tool2)
        engine.register_tool("tool3", tool3)
        engine.register_tool("tool4", tool4)
        
        # When
        result = await engine.execute(workflow, {})
        
        # Then
        assert result["status"] == "completed"
        assert result["outputs"]["node1"]["step"] == 1
        assert result["outputs"]["node2"]["step"] == 2
        assert result["outputs"]["node3"]["step"] == 3
        assert result["outputs"]["node4"]["step"] == 4
